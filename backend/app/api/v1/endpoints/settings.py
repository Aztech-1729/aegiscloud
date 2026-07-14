from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import User, Setting
from app.schemas.schemas import SettingsUpdate, SettingsResponse
from app.api.deps.auth import get_current_user

router = APIRouter()


AVAILABLE_MODELS = {
    "models": ["gpt-4", "gpt-3.5-turbo", "claude-3"],
    "default": "gpt-4",
}


@router.get("/models")
async def get_models():
    return AVAILABLE_MODELS


@router.get("", response_model=SettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Setting).where(Setting.user_id == current_user.id)
    )
    user_settings = result.scalar_one_or_none()

    if not user_settings:
        user_settings = Setting(user_id=current_user.id)
        db.add(user_settings)
        await db.flush()

    return user_settings


@router.patch("", response_model=SettingsResponse)
async def update_settings(
    data: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Setting).where(Setting.user_id == current_user.id)
    )
    user_settings = result.scalar_one_or_none()

    if not user_settings:
        user_settings = Setting(user_id=current_user.id)
        db.add(user_settings)
        await db.flush()

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_settings, key, value)

    return user_settings
