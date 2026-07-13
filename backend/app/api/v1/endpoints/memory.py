"""Device Memory API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.memory.device_memory import device_memory
from app.api.deps.auth import get_current_user
from app.models.models import User

router = APIRouter()


@router.get("/{device_id}")
async def get_device_memory(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the AI memory for a device."""
    memory = await device_memory.get_memory(db=db, device_id=device_id)
    return memory


@router.get("/{device_id}/recommendations")
async def get_recommendations(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-generated recommendations for a device."""
    recommendations = await device_memory.generate_recommendations(
        db=db,
        device_id=device_id,
    )
    return {"recommendations": recommendations, "total": len(recommendations)}


@router.get("/{device_id}/ai-context")
async def get_ai_context(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI context string for a device."""
    context = await device_memory.get_ai_context(db=db, device_id=device_id)
    return {"context": context}


@router.post("/{device_id}/preferences")
async def update_preferences(
    device_id: str,
    preferences: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user preferences for a device."""
    await device_memory.update_preferences(
        db=db,
        device_id=device_id,
        preferences=preferences,
    )
    return {"message": "Preferences updated"}
