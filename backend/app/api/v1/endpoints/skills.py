"""Skills API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.skills.engine import skill_engine
from app.api.deps.auth import get_current_user
from app.models.models import User

router = APIRouter()


@router.get("")
async def list_skills(
    category: str = None,
    search: str = None,
    current_user: User = Depends(get_current_user),
):
    """List all available skills."""
    skills = skill_engine.list_skills(category=category, search=search)
    return {"skills": skills, "total": len(skills)}


@router.get("/categories")
async def list_skill_categories(current_user: User = Depends(get_current_user)):
    """List all skill categories."""
    return {"categories": skill_engine.get_skill_categories()}


@router.get("/{skill_id}")
async def get_skill(skill_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific skill."""
    skill = skill_engine.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.post("/{skill_id}/execute")
async def execute_skill(
    skill_id: str,
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute a skill on a device."""
    try:
        result = await skill_engine.execute_skill(
            db=db,
            user_id=current_user.id,
            device_id=device_id,
            skill_id=skill_id,
            user_plan=current_user.plan,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
