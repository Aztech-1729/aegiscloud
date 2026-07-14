"""Marketplace API Endpoints

Public API for browsing, downloading, and publishing plugins.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import hashlib
import json

from app.db.session import get_db
from app.models.models import Plugin, User
from app.api.deps.auth import get_current_user
from app.services.plugins.validator import plugin_validator
from app.schemas.schemas import PluginManifest, PluginListing

router = APIRouter()


@router.get("")
async def list_plugins(
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "popular",
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List all plugins."""
    query = select(Plugin)

    if category:
        query = query.where(Plugin.category == category)

    if search:
        query = query.where(
            Plugin.name.ilike(f"%{search}%") |
            Plugin.description.ilike(f"%{search}%")
        )

    if sort_by == "popular":
        query = query.order_by(Plugin.download_count.desc())
    elif sort_by == "rating":
        query = query.order_by(Plugin.rating.desc())
    elif sort_by == "newest":
        query = query.order_by(Plugin.created_at.desc())

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    plugins = result.scalars().all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "version": p.version,
            "author": p.author,
            "description": p.description,
            "category": p.category,
            "download_count": p.download_count,
            "rating": p.rating,
            "size_mb": p.size_mb,
            "tools": p.tools or [],
            "published_at": p.created_at.isoformat(),
        }
        for p in plugins
    ]


@router.get("/{plugin_id}")
async def get_plugin(
    plugin_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a plugin."""
    result = await db.execute(
        select(Plugin).where(Plugin.plugin_id == plugin_id)
    )
    plugin = result.scalar_one_or_none()

    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")

    return {
        "id": plugin.id,
        "plugin_id": plugin.plugin_id,
        "name": plugin.name,
        "author": plugin.author,
        "description": plugin.description,
        "category": plugin.category,
        "version": plugin.version,
        "download_count": plugin.download_count,
        "rating": plugin.rating,
        "tools": plugin.tools or [],
        "size_mb": plugin.size_mb,
        "created_at": plugin.created_at.isoformat(),
    }


@router.post("/publish")
async def publish_plugin(
    file: UploadFile = File(...),
    api_key: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Publish a new plugin or update an existing one."""
    # Verify API key
    result = await db.execute(select(User).where(User.api_key == api_key))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Read uploaded file
    contents = await file.read()
    
    # Validate file size (max 10MB)
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")
    
    # Deserialize plugin package
    try:
        plugin_data = json.loads(contents.decode('utf-8'))
    except:
        # Try to parse as binary format
        plugin_data = json.loads(contents)
    
    # Validate plugin
    validation = await plugin_validator.validate_plugin(plugin_data)
    
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail={
                "errors": validation["errors"],
                "warnings": validation["warnings"],
            }
        )
    
    # Generate signature
    binary = plugin_data["binary"]
    binary_hash = hashlib.sha256(binary).hexdigest()
    
    # TODO: Sign with Aegis CA private key
    signature = f"aegis_signature_{binary_hash[:16]}"
    
    # Publish plugin
    plugin = await plugin_validator.publish_plugin(
        db=db,
        plugin_data=plugin_data,
        author_id=user.id,
        signature=signature,
    )
    
    return {
        "id": plugin.id,
        "plugin_id": plugin.plugin_id,
        "version": plugin.version,
        "message": "Plugin published successfully",
        "warnings": validation["warnings"],
    }


@router.post("/{plugin_id}/download")
async def download_plugin(
    plugin_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Download a plugin."""
    result = await db.execute(
        select(Plugin).where(Plugin.plugin_id == plugin_id)
    )
    plugin = result.scalar_one_or_none()

    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")

    plugin.download_count = (plugin.download_count or 0) + 1
    await db.commit()

    return {
        "id": plugin.id,
        "name": plugin.name,
        "version": plugin.version,
        "author": plugin.author,
        "description": plugin.description,
        "tools": plugin.tools or [],
        "download_count": plugin.download_count,
        "size_mb": plugin.size_mb,
    }


@router.post("/{plugin_id}/rate")
async def rate_plugin(
    plugin_id: str,
    rating: int = Form(...),
    comment: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Rate a plugin."""
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    result = await db.execute(
        select(Plugin).where(Plugin.plugin_id == plugin_id)
    )
    plugin = result.scalar_one_or_none()

    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")

    plugin.rating = float(rating)

    await db.commit()

    return {
        "message": "Rating submitted",
        "plugin_rating": plugin.rating,
    }


@router.get("/categories")
async def list_categories():
    """List all plugin categories."""
    return {
        "categories": [
            {"id": "system", "name": "System", "description": "System utilities and information"},
            {"id": "process", "name": "Process", "description": "Process management tools"},
            {"id": "file", "name": "File", "description": "File operations"},
            {"id": "network", "name": "Network", "description": "Network utilities"},
            {"id": "security", "name": "Security", "description": "Security tools"},
            {"id": "maintenance", "name": "Maintenance", "description": "System maintenance"},
            {"id": "diagnostic", "name": "Diagnostic", "description": "Diagnostic tools"},
            {"id": "monitoring", "name": "Monitoring", "description": "Monitoring tools"},
            {"id": "custom", "name": "Custom", "description": "Custom tools"},
        ]
    }
