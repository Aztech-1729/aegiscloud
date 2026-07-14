from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.models import User, Device, DeviceStatus
from app.schemas.schemas import ChatRequest, ChatResponse
from app.api.deps.auth import get_current_user
from app.services.ai import AIService

router = APIRouter()
ai_service = AIService()


@router.get("/suggestions")
async def get_suggestions():
    return {
        "suggestions": [
            {"icon": "Zap", "label": "Check CPU Performance", "prompt": "Show me the current CPU usage on all my devices"},
            {"icon": "Settings", "label": "Run System Cleanup", "prompt": "Run a system cleanup on my devices - clean temp files and empty recycle bin"},
            {"icon": "HardDrive", "label": "Analyze Storage", "prompt": "Analyze disk space usage across all connected devices"},
            {"icon": "Monitor", "label": "Monitor Network", "prompt": "Show me network information and status for my devices"},
            {"icon": "Sparkles", "label": "Quick Health Check", "prompt": "Run a health check on all my devices - CPU, RAM, disk, and network"},
            {"icon": "Bot", "label": "List Running Tasks", "prompt": "What tasks are currently running on my devices?"},
        ]
    }


@router.post("/chat", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    if data.device_id:
        result = await db.execute(
            select(Device).where(Device.id == data.device_id, Device.user_id == current_user.id)
        )
        device = result.scalar_one_or_none()
    else:
        result = await db.execute(
            select(Device).where(Device.user_id == current_user.id).order_by(Device.created_at.desc())
        )
        device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.status != DeviceStatus.online:
        raise HTTPException(status_code=400, detail="Device is not online")

    response = await ai_service.process_message(data.message, device.name)
    return response
