from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
from typing import Dict, Set
import asyncio

from app.db.session import async_session_factory
from app.core.security import decode_token
from app.models.models import User, Device, DeviceStatus, DeviceSession
from app.core.logging import get_logger
from datetime import datetime, timezone

logger = get_logger(__name__)
router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.device_connections: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, connection_id: str, device_id: str = None):
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        if device_id:
            if device_id not in self.device_connections:
                self.device_connections[device_id] = set()
            self.device_connections[device_id].add(connection_id)

    def disconnect(self, connection_id: str, device_id: str = None):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if device_id and device_id in self.device_connections:
            self.device_connections[device_id].discard(connection_id)
            if not self.device_connections[device_id]:
                del self.device_connections[device_id]

    async def send_to_connection(self, connection_id: str, message: dict):
        if connection_id in self.active_connections:
            await self.active_connections[connection_id].send_json(message)

    async def send_to_device(self, device_id: str, message: dict):
        if device_id in self.device_connections:
            for conn_id in self.device_connections[device_id]:
                await self.send_to_connection(conn_id, message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    import secrets
    connection_id = secrets.token_urlsafe(16)

    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid token")
        return

    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=4001, reason="Invalid token")
        return

    async with async_session_factory() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            await websocket.close(code=4001, reason="User not found")
            return

    await manager.connect(websocket, connection_id)
    logger.info(f"WebSocket connected: {connection_id} for user {user_id}")

    await manager.send_to_connection(connection_id, {
        "type": "connected",
        "connection_id": connection_id,
    })

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type")

            if msg_type == "subscribe_device":
                device_id = message.get("device_id")
                await manager.connect(websocket, connection_id, device_id)
                await manager.send_to_connection(connection_id, {
                    "type": "subscribed",
                    "device_id": device_id,
                })

            elif msg_type == "heartbeat":
                await manager.send_to_connection(connection_id, {
                    "type": "heartbeat_ack",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

            elif msg_type == "task_update":
                device_id = message.get("device_id")
                if device_id:
                    await manager.send_to_device(device_id, {
                        "type": "task_progress",
                        "task_id": message.get("task_id"),
                        "progress": message.get("progress"),
                        "status": message.get("status"),
                    })

            elif msg_type == "live_stats":
                device_id = message.get("device_id")
                if device_id:
                    await manager.send_to_device(device_id, {
                        "type": "live_stats",
                        "device_id": device_id,
                        "stats": message.get("stats"),
                    })

            elif msg_type == "notification":
                await manager.send_to_connection(connection_id, {
                    "type": "notification",
                    "notification": message.get("notification"),
                })

            else:
                await manager.send_to_connection(connection_id, {
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}",
                })

    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(connection_id)


@router.websocket("/ws/agent")
async def agent_websocket(websocket: WebSocket, device_token: str = Query(...)):
    import secrets
    connection_id = secrets.token_urlsafe(16)

    async with async_session_factory() as db:
        result = await db.execute(
            select(Device).where(Device.device_token == device_token)
        )
        device = result.scalar_one_or_none()
        if not device:
            await websocket.close(code=4001, reason="Invalid device token")
            return

        device.status = DeviceStatus.online
        device.last_seen = datetime.now(timezone.utc)

        session = DeviceSession(device_id=device.id, websocket_id=connection_id)
        db.add(session)
        await db.commit()
        device_id = device.id
        user_id = device.user_id

    await manager.connect(websocket, connection_id, device_id)

    await manager.broadcast({
        "type": "device_connected",
        "device_id": device_id,
    })

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type")

            if msg_type == "heartbeat":
                async with async_session_factory() as db:
                    result = await db.execute(select(Device).where(Device.id == device_id))
                    dev = result.scalar_one_or_none()
                    if dev:
                        dev.last_seen = datetime.now(timezone.utc)
                        if "stats" in message:
                            dev.uptime = message["stats"].get("uptime", dev.uptime)
                        await db.commit()

            elif msg_type == "task_result":
                await manager.send_to_device(device_id, {
                    "type": "task_completed",
                    "task_id": message.get("task_id"),
                    "result": message.get("result"),
                })

            elif msg_type == "live_stats":
                await manager.broadcast({
                    "type": "live_stats",
                    "device_id": device_id,
                    "stats": message.get("stats"),
                })

            elif msg_type == "task_progress":
                await manager.broadcast({
                    "type": "task_progress",
                    "device_id": device_id,
                    "task_id": message.get("task_id"),
                    "progress": message.get("progress"),
                })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Agent WebSocket error: {e}")
    finally:
        manager.disconnect(connection_id, device_id)
        async with async_session_factory() as db:
            result = await db.execute(select(Device).where(Device.id == device_id))
            dev = result.scalar_one_or_none()
            if dev:
                dev.status = DeviceStatus.offline
                await db.commit()

        await manager.broadcast({
            "type": "device_disconnected",
            "device_id": device_id,
        })
