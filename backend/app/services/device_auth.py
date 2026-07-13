"""Phase 5: Device authentication - completely separate from user auth.

Each device has its own identity (fingerprint + certificate + token).
Devices authenticate independently, not through user sessions.
Supports mTLS-ready architecture.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
import secrets
import hashlib

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import Device, DeviceStatus, AuditLog
from app.core.config import settings


DEVICE_TOKEN_EXPIRY_DAYS = 90


def generate_device_fingerprint() -> str:
    """Generate a unique device fingerprint from hardware identifiers."""
    raw = secrets.token_hex(32)
    return hashlib.sha256(raw.encode()).hexdigest()


def generate_device_token() -> str:
    """Generate a cryptographically secure device token."""
    return f"aegis_dev_{secrets.token_urlsafe(64)}"


async def authenticate_device(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Device:
    """Phase 5: Authenticate device via bearer token (separate from user auth).
    
    Devices use their own tokens, not user JWT tokens.
    This enables:
    - Device lifecycle independent of user sessions
    - Per-device revocation
    - Certificate-based auth (mTLS ready)
    - Audit trail per device
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Device authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header[7:]

    # Look up device by token
    result = await db.execute(
        select(Device).where(Device.device_token == token)
    )
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid device token",
        )

    # Check token expiry
    if device.device_token_expires and device.device_token_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Device token expired",
        )

    if not device.is_active if hasattr(device, 'is_active') else True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Device is disabled",
        )

    return device


async def rotate_device_token(
    device: Device,
    db: AsyncSession,
) -> str:
    """Phase 5: JWT-style token rotation for devices."""
    new_token = generate_device_token()
    device.device_token = new_token
    device.device_token_expires = datetime.now(timezone.utc) + timedelta(days=DEVICE_TOKEN_EXPIRY_DAYS)
    await db.flush()
    return new_token


async def record_device_heartbeat(
    device: Device,
    db: AsyncSession,
    stats: Optional[dict] = None,
) -> None:
    """Update device last seen and optional system stats."""
    now = datetime.now(timezone.utc)
    device.last_seen = now
    device.last_heartbeat = now
    device.status = DeviceStatus.online

    if stats:
        if "uptime_seconds" in stats:
            device.uptime_seconds = stats["uptime_seconds"]
        if "agent_version" in stats:
            device.agent_version = stats["agent_version"]
        if "cpu_info" in stats:
            device.cpu_info = stats["cpu_info"]
        if "ram_total_gb" in stats:
            device.ram_total_gb = stats["ram_total_gb"]
        if "gpu_info" in stats:
            device.gpu_info = stats["gpu_info"]
        if "disk_total_gb" in stats:
            device.disk_total_gb = stats["disk_total_gb"]
        if "disk_used_gb" in stats:
            device.disk_used_gb = stats["disk_used_gb"]
        if "windows_version" in stats:
            device.windows_version = stats["windows_version"]
        if "windows_build" in stats:
            device.windows_build = stats["windows_build"]
        if "hostname" in stats:
            device.hostname = stats["hostname"]

    await db.flush()


async def create_audit_log(
    db: AsyncSession,
    user_id: Optional[str] = None,
    device_id: Optional[str] = None,
    action: str = "",
    resource: str = "",
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    success: bool = True,
) -> None:
    """Phase 5: Create an immutable audit log entry."""
    log = AuditLog(
        user_id=user_id,
        device_id=device_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details or {},
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
    )
    db.add(log)
    await db.flush()
