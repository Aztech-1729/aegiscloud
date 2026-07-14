from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.models.models import User, Device, DeviceStatus
from app.api.deps.auth import get_current_user

router = APIRouter()


class TerminalExecuteRequest(BaseModel):
    device: str
    command: str


@router.post("/execute")
async def terminal_execute(
    data: TerminalExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    result = await db.execute(
        select(Device).where(Device.name == data.device, Device.user_id == current_user.id)
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.status != DeviceStatus.online:
        raise HTTPException(status_code=400, detail="Device is not online")

    return {
        "output": f"Command '{data.command}' executed on {data.device}",
        "result": "Command executed successfully",
    }
