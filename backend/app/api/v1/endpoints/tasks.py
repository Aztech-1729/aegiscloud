from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.models import User, Device, Command, CommandStatus
from app.schemas.schemas import TaskCreate, TaskResponse
from app.api.deps.auth import get_current_user

router = APIRouter()


ALLOWED_TOOLS = {
    "system_info", "cpu_usage", "ram_usage", "gpu_usage", "disk_usage",
    "clean_temp", "empty_recycle_bin", "flush_dns", "restart_explorer", "storage_analysis",
    "list_processes", "kill_process",
    "list_services", "start_service", "stop_service", "restart_service",
    "list_startup", "enable_startup", "disable_startup",
    "search_files", "download_file", "upload_file", "delete_file", "rename_file", "move_file",
    "network_info", "wifi_info", "public_ip", "local_ip",
    "installed_apps", "uninstall_app",
    "defender_status", "firewall_status", "windows_update_status",
    "run_sfc", "run_dism",
}


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    device_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Command).where(Command.user_id == current_user.id)
    if device_id:
        query = query.where(Command.device_id == device_id)
    if status:
        query = query.where(Command.status == status)
    query = query.order_by(Command.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Command).where(Command.id == task_id, Command.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("", response_model=TaskResponse)
async def create_task(
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if data.tool_name not in ALLOWED_TOOLS:
        raise HTTPException(status_code=400, detail=f"Tool '{data.tool_name}' is not allowed")

    device_result = await db.execute(
        select(Device).where(Device.id == data.device_id, Device.user_id == current_user.id)
    )
    device = device_result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.status != "online":
        raise HTTPException(status_code=400, detail="Device is not online")

    task = Command(
        user_id=current_user.id,
        device_id=data.device_id,
        tool_name=data.tool_name,
        parameters=data.parameters,
        status=CommandStatus.pending,
    )
    db.add(task)
    await db.flush()

    return task


@router.post("/{task_id}/cancel", response_model=TaskResponse)
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Command).where(Command.id == task_id, Command.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status not in (CommandStatus.pending, CommandStatus.running):
        raise HTTPException(status_code=400, detail="Task cannot be cancelled")

    task.status = CommandStatus.cancelled
    task.completed_at = datetime.now(timezone.utc)
    return task


@router.post("/{task_id}/retry", response_model=TaskResponse)
async def retry_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Command).where(Command.id == task_id, Command.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = CommandStatus.pending
    task.progress = 0
    task.result = None
    task.error_message = None
    task.started_at = None
    task.completed_at = None
    return task
