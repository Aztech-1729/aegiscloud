"""Plugins API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.plugins.registry import plugin_manager
from app.api.deps.auth import get_current_user
from app.models.models import User

router = APIRouter()


@router.get("")
async def list_plugins(
    category: str = None,
    current_user: User = Depends(get_current_user),
):
    """List all available plugins."""
    plugins = plugin_manager.list_available_plugins(category=category)
    return {"plugins": plugins, "total": len(plugins)}


@router.get("/installed")
async def list_installed_plugins(
    device_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List installed plugins for the user."""
    plugins = await plugin_manager.get_installed_plugins(
        db=db,
        user_id=current_user.id,
        device_id=device_id,
    )
    return {"plugins": plugins, "total": len(plugins)}


@router.post("/{plugin_id}/install")
async def install_plugin(
    plugin_id: str,
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Install a plugin on a device."""
    try:
        result = await plugin_manager.install_plugin(
            db=db,
            user_id=current_user.id,
            device_id=device_id,
            plugin_id=plugin_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{plugin_id}/uninstall")
async def uninstall_plugin(
    plugin_id: str,
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Uninstall a plugin from a device."""
    try:
        result = await plugin_manager.uninstall_plugin(
            db=db,
            user_id=current_user.id,
            device_id=device_id,
            plugin_id=plugin_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
