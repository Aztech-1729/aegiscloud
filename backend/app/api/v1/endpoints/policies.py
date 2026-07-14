"""Policies API endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.db.session import get_db
from app.services.policies.engine import policy_engine
from app.api.deps.auth import get_current_user
from app.models.models import User, Policy

router = APIRouter()


class PolicyCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    category: Optional[str] = "custom"
    condition: dict = {}
    active: Optional[bool] = False


@router.get("")
async def list_policies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all policies for the user."""
    result = await db.execute(
        select(Policy).where(Policy.user_id == current_user.id)
    )
    policies = result.scalars().all()
    return {"policies": [p.dict() for p in policies], "total": len(policies)}


@router.post("")
async def create_policy(
    data: PolicyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    policy = Policy(
        user_id=current_user.id,
        name=data.name,
        description=data.description or "",
        category=data.category or "custom",
        condition=data.condition,
        actions=[],
        is_active=data.active,
    )
    db.add(policy)
    await db.flush()
    return {
        "id": policy.id,
        "name": policy.name,
        "description": policy.description,
        "category": policy.category,
        "condition": policy.condition,
        "active": policy.is_active,
        "triggered": 0,
        "lastTriggered": "Never",
    }


@router.get("/templates")
async def list_policy_templates(current_user: User = Depends(get_current_user)):
    """List all policy templates."""
    return {"templates": policy_engine.get_templates()}


@router.get("/templates/{template_id}")
async def get_policy_template(template_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific policy template."""
    template = policy_engine.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/create-from-template/{template_id}")
async def create_policy_from_template(
    template_id: str,
    device_ids: list[str],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create policies from a template for specified devices."""
    try:
        policies = await policy_engine.create_from_template(
            db=db,
            user_id=current_user.id,
            template_id=template_id,
            device_ids=device_ids,
        )
        return {"policies": [p.dict() for p in policies], "created": len(policies)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{policy_id}/toggle")
async def toggle_policy(
    policy_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Enable or disable a policy."""
    result = await db.execute(
        select(Policy).where(Policy.id == policy_id, Policy.user_id == current_user.id)
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    policy.is_active = not policy.is_active
    await db.commit()

    return {"policy_id": policy_id, "is_active": policy.is_active}


@router.delete("/{policy_id}")
async def delete_policy(
    policy_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a policy."""
    result = await db.execute(
        select(Policy).where(Policy.id == policy_id, Policy.user_id == current_user.id)
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    await db.delete(policy)
    await db.commit()

    return {"message": "Policy deleted"}
