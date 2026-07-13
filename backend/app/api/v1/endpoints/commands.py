"""Phase 3-4: Command endpoints with full lifecycle management."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import User, Device, Command, CommandStatus, CommandPriority
from app.schemas.schemas import TaskResponse
from app.api.deps.auth import get_current_user
from app.services.command_queue import command_queue
from app.services.tool_registry import tool_registry, ToolValidationError
from app.services.device_auth import create_audit_log

router = APIRouter()


class CommandCreate:
    def __init__(self, device_id: str, tool_name: str, parameters: dict = None, priority: str = "normal"):
        self.device_id = device_id
        self.tool_name = tool_name
        self.parameters = parameters or {}
        self.priority = priority


@router.post("", response_model=dict)
async def create_command(
    device_id: str,
    tool_name: str,
    parameters: dict = None,
    priority: str = "normal",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Queue a new command for execution on a device.
    
    Phase 3: Validates tool against registry, checks parameters,
    and creates a command with proper lifecycle tracking.
    """
    try:
        command = await command_queue.enqueue(
            db=db,
            user_id=current_user.id,
            device_id=device_id,
            tool_name=tool_name,
            parameters=parameters or {},
            user_plan=current_user.plan.value,
            priority=CommandPriority(priority) if priority in [e.value for e in CommandPriority] else CommandPriority.normal,
        )
        return {
            "id": command.id,
            "status": command.status.value,
            "tool_name": command.tool_name,
            "requires_approval": command.requires_approval,
            "message": "Command queued" if not command.requires_approval else "Awaiting approval",
        }
    except ToolValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[dict])
async def list_commands(
    device_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List commands with filtering."""
    query = select(Command).where(Command.user_id == current_user.id)
    if device_id:
        query = query.where(Command.device_id == device_id)
    if status:
        query = query.where(Command.status == status)
    query = query.order_by(Command.created_at.desc()).limit(limit)

    result = await db.execute(query)
    commands = result.scalars().all()

    return [
        {
            "id": c.id,
            "device_id": c.device_id,
            "tool_name": c.tool_name,
            "status": c.status.value,
            "progress": c.progress,
            "result": c.result,
            "error_message": c.error_message,
            "requires_approval": c.requires_approval,
            "queued_at": c.queued_at.isoformat() if c.queued_at else None,
            "started_at": c.started_at.isoformat() if c.started_at else None,
            "completed_at": c.completed_at.isoformat() if c.completed_at else None,
        }
        for c in commands
    ]


@router.get("/{command_id}")
async def get_command(
    command_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get command details."""
    result = await db.execute(
        select(Command).where(Command.id == command_id, Command.user_id == current_user.id)
    )
    command = result.scalar_one_or_none()
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")

    return {
        "id": command.id,
        "device_id": command.device_id,
        "tool_name": command.tool_name,
        "tool_version": command.tool_version,
        "status": command.status.value,
        "priority": command.priority.value,
        "parameters": command.parameters,
        "progress": command.progress,
        "result": command.result,
        "error_message": command.error_message,
        "error_code": command.error_code,
        "logs": command.logs,
        "requires_approval": command.requires_approval,
        "approved_by": command.approved_by,
        "approved_at": command.approved_at.isoformat() if command.approved_at else None,
        "queued_at": command.queued_at.isoformat() if command.queued_at else None,
        "sent_at": command.sent_at.isoformat() if command.sent_at else None,
        "started_at": command.started_at.isoformat() if command.started_at else None,
        "completed_at": command.completed_at.isoformat() if command.completed_at else None,
        "timeout_seconds": command.timeout_seconds,
        "nonce": command.nonce,
    }


@router.post("/{command_id}/cancel")
async def cancel_command(
    command_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a queued or running command."""
    try:
        command = await command_queue.cancel(db, command_id, current_user.id)
        return {"id": command.id, "status": "cancelled", "message": "Command cancelled"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{command_id}/retry")
async def retry_command(
    command_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retry a failed command."""
    try:
        new_command = await command_queue.retry(db, command_id, current_user.id)
        return {"id": new_command.id, "status": new_command.status.value, "message": "Command retried"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{command_id}/approve")
async def approve_command(
    command_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve a command that requires approval (Phase 5)."""
    try:
        command = await command_queue.approve(db, command_id, current_user.id)
        return {"id": command.id, "status": "queued", "message": "Command approved and queued"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
