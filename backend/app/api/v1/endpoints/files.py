from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import User, Device
from app.api.deps.auth import get_current_user

router = APIRouter()


@router.get("")
async def list_files_root(
    path: str = "~/Desktop",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    devices = await db.execute(
        select(Device).where(Device.user_id == current_user.id)
    )
    user_devices = devices.scalars().all()

    mock_files = [
        {"name": "Documents", "path": f"{path}/Documents", "type": "folder", "size": 0, "modified": "2024-01-15", "is_directory": True},
        {"name": "Downloads", "path": f"{path}/Downloads", "type": "folder", "size": 0, "modified": "2024-01-14", "is_directory": True},
        {"name": "report.docx", "path": f"{path}/report.docx", "type": "file", "size": 2457600, "modified": "2024-01-15", "is_directory": False},
        {"name": "notes.txt", "path": f"{path}/notes.txt", "type": "file", "size": 4096, "modified": "2024-01-13", "is_directory": False},
    ]
    return mock_files


class FileEntry:
    def __init__(self, name: str, path: str, type: str, size: int, modified: str, is_directory: bool):
        self.name = name
        self.path = path
        self.type = type
        self.size = size
        self.modified = modified
        self.is_directory = is_directory


@router.get("/{device_id}")
async def list_files(
    device_id: str,
    path: str = "~/Desktop",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Device).where(Device.id == device_id, Device.user_id == current_user.id)
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.status != "online":
        raise HTTPException(status_code=400, detail="Device is not online")

    mock_files = [
        {"name": "Documents", "path": f"{path}/Documents", "type": "folder", "size": 0, "modified": "2024-01-15", "is_directory": True},
        {"name": "Downloads", "path": f"{path}/Downloads", "type": "folder", "size": 0, "modified": "2024-01-14", "is_directory": True},
        {"name": "report.docx", "path": f"{path}/report.docx", "type": "file", "size": 2457600, "modified": "2024-01-15", "is_directory": False},
        {"name": "notes.txt", "path": f"{path}/notes.txt", "type": "file", "size": 4096, "modified": "2024-01-13", "is_directory": False},
    ]
    return mock_files


@router.delete("/{device_id}")
async def delete_file(
    device_id: str,
    path: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Device).where(Device.id == device_id, Device.user_id == current_user.id)
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return {"message": f"File deletion queued for: {path}"}
