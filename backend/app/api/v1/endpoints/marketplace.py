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
from app.models.models import Plugin, PluginVersion, User
from app.api.v1.deps.auth import get_current_user
from app.services.plugins.validator import plugin_validator
from app.schemas.schemas import PluginManifest, PluginListing

router = APIRouter()


@router.get("/plugins", response_model=List[PluginListing])
async def list_plugins(
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "popular",
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List all published plugins."""
    query = select(Plugin).where(Plugin.is_published == True)
    
    if category:
        query = query.where(Plugin.category == category)
    
    if search:
        query = query.where(
            Plugin.name.ilike(f"%{search}%") | 
            Plugin.description.ilike(f"%{search}%")
        )
    
    # Apply sorting
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
        PluginListing(
            id=p.id,
            name=p.name,
            version=p.latest_version.version,
            author=p.author.name,
            description=p.description,
            category=p.category,
            download_count=p.download_count,
            rating=p.rating,
            rating_count=p.rating_count,
            size_bytes=p.latest_version.size_bytes,
            published_at=p.created_at.isoformat(),
            updated_at=p.updated_at.isoformat(),
            tools=[t.name for t in p.latest_version.manifest.tools],
            tags=p.tags,
        )
        for p in plugins
    ]


@router.get("/plugins/{plugin_id}")
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
    
    # Increment view count
    plugin.view_count = (plugin.view_count or 0) + 1
    
    return {
        "id": plugin.id,
        "plugin_id": plugin.plugin_id,
        "name": plugin.name,
        "author": plugin.author.name,
        "description": plugin.description,
        "homepage": plugin.homepage,
        "repository": plugin.repository,
        "license": plugin.license,
        "category": plugin.category,
        "version": plugin.latest_version.version,
        "download_count": plugin.download_count,
        "rating": plugin.rating,
        "rating_count": plugin.rating_count,
        "tools": [
            {
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "risk_level": t.risk_level,
                "requires_approval": t.requires_approval,
            }
            for t in plugin.latest_version.manifest.tools
        ],
        "versions": [
            {
                "version": v.version,
                "published_at": v.created_at.isoformat(),
                "size_bytes": v.size_bytes,
            }
            for v in plugin.versions
        ],
        "reviews": [
            {
                "user": r.user.name,
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at.isoformat(),
            }
            for r in plugin.reviews[:10]
        ],
    }


@router.post("/plugins/publish")
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
        "version": plugin.latest_version.version,
        "message": "Plugin published successfully",
        "warnings": validation["warnings"],
    }


@router.post("/plugins/{plugin_id}/download")
async def download_plugin(
    plugin_id: str,
    version: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Download a plugin binary."""
    result = await db.execute(
        select(Plugin).where(Plugin.plugin_id == plugin_id)
    )
    plugin = result.scalar_one_or_none()
    
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    
    # Get version
    if version:
        result = await db.execute(
            select(PluginVersion).where(
                PluginVersion.plugin_id == plugin.id,
                PluginVersion.version == version,
            )
        )
        plugin_version = result.scalar_one_or_none()
    else:
        plugin_version = plugin.latest_version
    
    if not plugin_version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Increment download count
    plugin.download_count = (plugin.download_count or 0) + 1
    plugin_version.download_count = (plugin_version.download_count or 0) + 1
    
    # Return plugin package
    return {
        "manifest": plugin_version.manifest,
        "binary": plugin_version.binary,
        "binary_hash": plugin_version.binary_hash,
        "signature": plugin_version.signature,
    }


@router.post("/plugins/{plugin_id}/rate")
async def rate_plugin(
    plugin_id: str,
    rating: int = Form(...),
    comment: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Rate and review a plugin."""
    # Validate rating
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    result = await db.execute(
        select(Plugin).where(Plugin.plugin_id == plugin_id)
    )
    plugin = result.scalar_one_or_none()
    
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    
    # Create or update review
    from app.models.models import PluginReview
    
    result = await db.execute(
        select(PluginReview).where(
            PluginReview.plugin_id == plugin.id,
            PluginReview.user_id == current_user.id,
        )
    )
    review = result.scalar_one_or_none()
    
    if review:
        review.rating = rating
        review.comment = comment
    else:
        review = PluginReview(
            plugin_id=plugin.id,
            user_id=current_user.id,
            rating=rating,
            comment=comment,
        )
        db.add(review)
    
    # Update plugin rating
    result = await db.execute(
        select(
            func.avg(PluginReview.rating),
            func.count(PluginReview.id),
        ).where(PluginReview.plugin_id == plugin.id)
    )
    avg_rating, rating_count = result.one()
    
    plugin.rating = float(avg_rating) if avg_rating else 0.0
    plugin.rating_count = rating_count or 0
    
    await db.commit()
    
    return {
        "message": "Rating submitted",
        "plugin_rating": plugin.rating,
        "rating_count": plugin.rating_count,
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
