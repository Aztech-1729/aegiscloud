from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.models import User, Device, DeviceStatus
from app.schemas.schemas import ChatRequest, ChatResponse
from app.api.deps.auth import get_current_user
from app.services.ai import AIService

router = APIRouter()
ai_service = AIService()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    device_result = await db.execute(
        Device.__table__.select()
        .where(Device.id == data.device_id)
        .where(Device.user_id == current_user.id)
    )
    from sqlalchemy import select
    result = await db.execute(
        select(Device).where(Device.id == data.device_id, Device.user_id == current_user.id)
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.status != DeviceStatus.online:
        raise HTTPException(status_code=400, detail="Device is not online")

    response = await ai_service.process_message(data.message, device.name)
    return response
