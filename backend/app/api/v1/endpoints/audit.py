"""Phase 5: Audit log endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import User, AuditLog
from app.api.deps.auth import get_current_user, get_admin_user

router = APIRouter()


@router.get("")
async def get_audit_logs(
    action: Optional[str] = None,
    resource: Optional[str] = None,
    device_id: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get audit logs for the current user."""
    query = select(AuditLog).where(AuditLog.user_id == current_user.id)
    if action:
        query = query.where(AuditLog.action == action)
    if resource:
        query = query.where(AuditLog.resource == resource)
    if device_id:
        query = query.where(AuditLog.device_id == device_id)
    query = query.order_by(AuditLog.timestamp.desc()).limit(limit)

    result = await db.execute(query)
    logs = result.scalars().all()

    return [
        {
            "id": log.id,
            "action": log.action,
            "resource": log.resource,
            "resource_id": log.resource_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "success": log.success,
            "timestamp": log.timestamp.isoformat(),
        }
        for log in logs
    ]


@router.get("/admin")
async def get_admin_audit_logs(
    limit: int = 200,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all audit logs (admin only)."""
    result = await db.execute(
        select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
    )
    logs = result.scalars().all()

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "device_id": log.device_id,
            "action": log.action,
            "resource": log.resource,
            "resource_id": log.resource_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "success": log.success,
            "timestamp": log.timestamp.isoformat(),
        }
        for log in logs
    ]
