"""Event Stream System — Real-time event pub/sub

Instead of polling, everything streams:
    Explorer crashed
        ↓
    Browser updates instantly
        ↓
    AI sees event
        ↓
    Suggests fix

Events are:
    - Device events (online, offline, heartbeat)
    - System events (process crash, service stop, high CPU)
    - Command events (started, completed, failed)
    - Security events (threat detected, firewall rule)
    - Update events (available, downloaded, installed)

All events flow through Redis pub/sub for real-time distribution.
"""
from datetime import datetime, timezone
from typing import Optional, Callable, Any
import json
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as redis

from app.db.session import get_db
from app.models.models import Event, Device
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EventStream:
    """Real-time event streaming system."""

    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.subscribers: dict[str, list[Callable]] = {}

    async def initialize(self):
        """Initialize Redis connection."""
        if not self.redis:
            self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def publish(
        self,
        event_type: str,
        device_id: str,
        user_id: str,
        data: dict,
        severity: str = "info",
    ) -> str:
        """Publish an event to the stream.
        
        Event Types:
            device.online / device.offline / device.heartbeat
            system.process_crash / system.service_stopped / system.high_cpu
            command.started / command.completed / command.failed
            security.threat_detected / security.firewall_rule
            update.available / update.downloaded / update.installed
            policy.triggered / policy.executed
            skill.started / skill.completed / skill.failed
        """
        await self.initialize()

        event = Event(
            event_type=event_type,
            device_id=device_id,
            user_id=user_id,
            data=data,
            severity=severity,
        )

        # Store in database for history
        async for db in get_db():
            db.add(event)
            await db.commit()
            break

        # Publish to Redis for real-time distribution
        channel = f"events:{user_id}"
        event_data = {
            "id": event.id,
            "type": event_type,
            "device_id": device_id,
            "data": data,
            "severity": severity,
            "timestamp": event.created_at.isoformat(),
        }

        await self.redis.publish(channel, json.dumps(event_data))

        # Also publish to device-specific channel
        device_channel = f"events:device:{device_id}"
        await self.redis.publish(device_channel, json.dumps(event_data))

        logger.info(f"Event published: {event_type} for device {device_id}")
        return event.id

    async def subscribe(
        self,
        user_id: str,
        callback: Callable,
        event_types: Optional[list[str]] = None,
    ):
        """Subscribe to events for a user.
        
        Args:
            user_id: User ID to subscribe to
            callback: Async function to call when event received
            event_types: Optional filter for specific event types
        """
        await self.initialize()

        channel = f"events:{user_id}"
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)

        logger.info(f"Subscribed to events for user {user_id}")

        async for message in pubsub.listen():
            if message["type"] == "message":
                event_data = json.loads(message["data"])

                # Filter by event type if specified
                if event_types and event_data.get("type") not in event_types:
                    continue

                await callback(event_data)

    async def get_recent_events(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 100,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> list[dict]:
        """Get recent events from database."""
        query = select(Event).where(Event.user_id == user_id)

        if event_type:
            query = query.where(Event.event_type == event_type)
        if severity:
            query = query.where(Event.severity == severity)

        query = query.order_by(Event.created_at.desc()).limit(limit)

        result = await db.execute(query)
        events = result.scalars().all()

        return [
            {
                "id": e.id,
                "type": e.event_type,
                "device_id": e.device_id,
                "data": e.data,
                "severity": e.severity,
                "timestamp": e.created_at.isoformat(),
            }
            for e in events
        ]


# Global event stream
event_stream = EventStream()


# ============= EVENT HELPERS =============

async def emit_device_online(device_id: str, user_id: str, device_info: dict):
    """Emit device online event."""
    await event_stream.publish(
        event_type="device.online",
        device_id=device_id,
        user_id=user_id,
        data=device_info,
        severity="info",
    )


async def emit_device_offline(device_id: str, user_id: str):
    """Emit device offline event."""
    await event_stream.publish(
        event_type="device.offline",
        device_id=device_id,
        user_id=user_id,
        data={},
        severity="warning",
    )


async def emit_command_completed(
    device_id: str,
    user_id: str,
    command_id: str,
    tool_name: str,
    success: bool,
    result: Optional[dict] = None,
):
    """Emit command completion event."""
    await event_stream.publish(
        event_type=f"command.{'completed' if success else 'failed'}",
        device_id=device_id,
        user_id=user_id,
        data={
            "command_id": command_id,
            "tool_name": tool_name,
            "success": success,
            "result": result,
        },
        severity="info" if success else "error",
    )


async def emit_security_alert(
    device_id: str,
    user_id: str,
    threat_type: str,
    details: dict,
):
    """Emit security alert event."""
    await event_stream.publish(
        event_type="security.threat_detected",
        device_id=device_id,
        user_id=user_id,
        data={
            "threat_type": threat_type,
            **details,
        },
        severity="critical",
    )


async def emit_policy_triggered(
    device_id: str,
    user_id: str,
    policy_id: str,
    policy_name: str,
    condition: dict,
    actions: list,
):
    """Emit policy triggered event."""
    await event_stream.publish(
        event_type="policy.triggered",
        device_id=device_id,
        user_id=user_id,
        data={
            "policy_id": policy_id,
            "policy_name": policy_name,
            "condition": condition,
            "actions": actions,
        },
        severity="warning",
    )
