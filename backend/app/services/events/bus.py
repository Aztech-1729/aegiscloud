"""Event Bus — Reactive system where everything is an event.

Architecture:
    CPU High
      ↓
    Event Bus
      ↓
    ┌─── Policy Engine → Restart Service → Notify Admin
    ├─── AI Assistant → Suggest Fix → User
    └─── Dashboard → Update UI → Real-time

Every action in the system produces events.
Every subsystem can subscribe to events.
This creates a fully reactive, decoupled architecture.

Event Types:
    - device.* (online, offline, heartbeat, stats_update)
    - command.* (queued, sent, running, completed, failed)
    - system.* (process_crash, service_stop, high_cpu, high_ram, low_disk)
    - security.* (threat_detected, firewall_change, defender_disabled)
    - policy.* (triggered, executed, failed)
    - skill.* (started, completed, failed)
    - update.* (available, downloading, installed)
    - network.* (disconnected, reconnecting, latency_spike)
    - user.* (login, logout, preference_change)
"""
from datetime import datetime, timezone
from typing import Optional, Callable, Any, Awaitable
from enum import Enum
import json
import asyncio
from dataclasses import dataclass, field

import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EventType(str, Enum):
    """All event types in the system."""
    # Device events
    DEVICE_ONLINE = "device.online"
    DEVICE_OFFLINE = "device.offline"
    DEVICE_HEARTBEAT = "device.heartbeat"
    DEVICE_STATS_UPDATE = "device.stats_update"
    DEVICE_TAG_CHANGE = "device.tag_change"
    
    # Command events
    COMMAND_QUEUED = "command.queued"
    COMMAND_SENT = "command.sent"
    COMMAND_RUNNING = "command.running"
    COMMAND_COMPLETED = "command.completed"
    COMMAND_FAILED = "command.failed"
    COMMAND_CANCELLED = "command.cancelled"
    COMMAND_APPROVED = "command.approved"
    
    # System events
    SYSTEM_PROCESS_CRASH = "system.process_crash"
    SYSTEM_SERVICE_STOP = "system.service_stop"
    SYSTEM_HIGH_CPU = "system.high_cpu"
    SYSTEM_HIGH_RAM = "system.high_ram"
    SYSTEM_LOW_DISK = "system.low_disk"
    SYSTEM_HIGH_TEMP = "system.high_temp"
    
    # Security events
    SECURITY_THREAT_DETECTED = "security.threat_detected"
    SECURITY_FIREWALL_CHANGE = "security.firewall_change"
    SECURITY_DEFENDER_DISABLED = "security.defender_disabled"
    
    # Policy events
    POLICY_TRIGGERED = "policy.triggered"
    POLICY_EXECUTED = "policy.executed"
    POLICY_FAILED = "policy.failed"
    
    # Skill events
    SKILL_STARTED = "skill.started"
    SKILL_COMPLETED = "skill.completed"
    SKILL_FAILED = "skill.failed"
    
    # Update events
    UPDATE_AVAILABLE = "update.available"
    UPDATE_DOWNLOADING = "update.downloading"
    UPDATE_INSTALLED = "update.installed"
    
    # Network events
    NETWORK_DISCONNECTED = "network.disconnected"
    NETWORK_RECONNECTING = "network.reconnecting"
    NETWORK_LATENCY_SPIKE = "network.latency_spike"
    
    # User events
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_PREFERENCE_CHANGE = "user.preference_change"


@dataclass
class Event:
    """An event in the system."""
    type: EventType
    device_id: str
    user_id: str
    data: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "agent"  # "agent", "server", "ai", "policy"
    correlation_id: Optional[str] = None  # Links related events
    
    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "device_id": self.device_id,
            "user_id": self.user_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "correlation_id": self.correlation_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        return cls(
            type=EventType(data["type"]),
            device_id=data["device_id"],
            user_id=data["user_id"],
            data=data.get("data", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            source=data.get("source", "unknown"),
            correlation_id=data.get("correlation_id"),
        )


class EventBus:
    """Central event bus for the entire platform.
    
    Handles:
    - Publishing events to Redis pub/sub
    - Subscribing to events
    - Event persistence for audit/history
    - Event routing to handlers
    """
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.handlers: dict[EventType, list[Callable[[Event], Awaitable[None]]]] = {}
        self.global_handlers: list[Callable[[Event], Awaitable[None]]] = []
    
    async def connect(self):
        """Connect to Redis."""
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        logger.info("Event bus connected to Redis")
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
    
    async def publish(self, event: Event) -> str:
        """Publish an event to the bus."""
        if not self.redis:
            await self.connect()
        
        # Publish to user-specific channel
        user_channel = f"events:user:{event.user_id}"
        await self.redis.publish(user_channel, json.dumps(event.to_dict()))
        
        # Publish to device-specific channel
        device_channel = f"events:device:{event.device_id}"
        await self.redis.publish(device_channel, json.dumps(event.to_dict()))
        
        # Publish to global channel (for admin/monitoring)
        await self.redis.publish("events:global", json.dumps(event.to_dict()))
        
        # Publish to type-specific channel (for policy engine, etc.)
        type_channel = f"events:type:{event.type.value}"
        await self.redis.publish(type_channel, json.dumps(event.to_dict()))
        
        # Dispatch to registered handlers
        await self._dispatch(event)
        
        logger.debug(f"Event published: {event.type.value} for device {event.device_id}")
        return event.correlation_id or ""
    
    async def _dispatch(self, event: Event):
        """Dispatch event to registered handlers."""
        # Type-specific handlers
        if event.type in self.handlers:
            for handler in self.handlers[event.type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Event handler error for {event.type.value}: {e}")
        
        # Global handlers
        for handler in self.global_handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Global event handler error: {e}")
    
    def on(self, event_type: EventType, handler: Callable[[Event], Awaitable[None]]):
        """Register a handler for a specific event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    def on_any(self, handler: Callable[[Event], Awaitable[None]]):
        """Register a handler for all events."""
        self.global_handlers.append(handler)
    
    async def subscribe_user(self, user_id: str) -> redis.client.PubSub:
        """Subscribe to all events for a user."""
        if not self.redis:
            await self.connect()
        
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(f"events:user:{user_id}")
        return pubsub
    
    async def subscribe_device(self, device_id: str) -> redis.client.PubSub:
        """Subscribe to all events for a device."""
        if not self.redis:
            await self.connect()
        
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(f"events:device:{device_id}")
        return pubsub
    
    async def get_recent_events(
        self,
        user_id: str,
        limit: int = 100,
        event_type: Optional[EventType] = None,
    ) -> list[Event]:
        """Get recent events from Redis list."""
        if not self.redis:
            await self.connect()
        
        key = f"events:history:{user_id}"
        events = await self.redis.lrange(key, 0, limit - 1)
        
        result = []
        for event_json in events:
            try:
                event = Event.from_dict(json.loads(event_json))
                if event_type is None or event.type == event_type:
                    result.append(event)
            except Exception as e:
                logger.error(f"Failed to parse event: {e}")
        
        return result
    
    async def store_event(self, event: Event, max_history: int = 1000):
        """Store event in Redis list for history."""
        if not self.redis:
            await self.connect()
        
        key = f"events:history:{event.user_id}"
        await self.redis.lpush(key, json.dumps(event.to_dict()))
        await self.redis.ltrim(key, 0, max_history - 1)


# ============= CONVENIENCE FUNCTIONS =============

async def emit_device_online(device_id: str, user_id: str, device_info: dict):
    """Emit device online event."""
    event = Event(
        type=EventType.DEVICE_ONLINE,
        device_id=device_id,
        user_id=user_id,
        data=device_info,
        source="server",
    )
    await event_bus.publish(event)


async def emit_device_offline(device_id: str, user_id: str):
    """Emit device offline event."""
    event = Event(
        type=EventType.DEVICE_OFFLINE,
        device_id=device_id,
        user_id=user_id,
        data={},
        source="server",
    )
    await event_bus.publish(event)


async def emit_command_completed(
    device_id: str,
    user_id: str,
    command_id: str,
    tool_name: str,
    success: bool,
    result: Optional[dict] = None,
):
    """Emit command completion event."""
    event = Event(
        type=EventType.COMMAND_COMPLETED if success else EventType.COMMAND_FAILED,
        device_id=device_id,
        user_id=user_id,
        data={
            "command_id": command_id,
            "tool_name": tool_name,
            "success": success,
            "result": result,
        },
        source="agent",
    )
    await event_bus.publish(event)


async def emit_system_alert(
    device_id: str,
    user_id: str,
    alert_type: EventType,
    data: dict,
):
    """Emit a system alert event."""
    event = Event(
        type=alert_type,
        device_id=device_id,
        user_id=user_id,
        data=data,
        source="agent",
    )
    await event_bus.publish(event)


async def emit_policy_triggered(
    device_id: str,
    user_id: str,
    policy_name: str,
    condition: dict,
    actions: list,
):
    """Emit policy triggered event."""
    event = Event(
        type=EventType.POLICY_TRIGGERED,
        device_id=device_id,
        user_id=user_id,
        data={
            "policy_name": policy_name,
            "condition": condition,
            "actions": actions,
        },
        source="policy",
    )
    await event_bus.publish(event)


async def emit_skill_execution(
    device_id: str,
    user_id: str,
    skill_name: str,
    status: str,
    details: Optional[dict] = None,
):
    """Emit skill execution event."""
    type_map = {
        "started": EventType.SKILL_STARTED,
        "completed": EventType.SKILL_COMPLETED,
        "failed": EventType.SKILL_FAILED,
    }
    event = Event(
        type=type_map.get(status, EventType.SKILL_STARTED),
        device_id=device_id,
        user_id=user_id,
        data={
            "skill_name": skill_name,
            "details": details or {},
        },
        source="ai",
    )
    await event_bus.publish(event)


# Global event bus instance
event_bus = EventBus()


# ============= DEFAULT HANDLERS =============

async def log_all_events(event: Event):
    """Log all events for debugging."""
    logger.info(
        f"EVENT: {event.type.value} | device={event.device_id} | "
        f"source={event.source} | data_keys={list(event.data.keys())}"
    )


async def store_events_for_audit(event: Event):
    """Store events for audit trail."""
    await event_bus.store_event(event)


def register_default_handlers():
    """Register default event handlers."""
    event_bus.on_any(store_events_for_audit)
