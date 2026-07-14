from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import User, Command
from app.schemas.schemas import TaskResponse
from app.api.deps.auth import get_current_user

router = APIRouter()


@router.get("", response_model=List[TaskResponse])
async def get_history(
    search: Optional[str] = None,
    status: Optional[str] = None,
    device_id: Optional[str] = None,
    page: int = 1,
    per_page: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Command).where(Command.user_id == current_user.id)

    if search:
        query = query.where(Command.tool_name.ilike(f"%{search}%"))
    if status:
        query = query.where(Command.status == status)
    if device_id:
        query = query.where(Command.device_id == device_id)

    query = query.order_by(Command.created_at.desc())
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/export")
async def export_history(
    format: str = "csv",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Command).where(Command.user_id == current_user.id).order_by(Command.created_at.desc())
    )
    tasks = result.scalars().all()

    if format == "csv":
        lines = ["id,tool_name,status,device_id,created_at,completed_at"]
        for task in tasks:
            lines.append(f"{task.id},{task.tool_name},{task.status},{task.device_id},{task.created_at},{task.completed_at}")
        content = "\n".join(lines)
        from fastapi.responses import Response
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=aegis_history.csv"},
        )

    return {"tasks": [{"id": t.id, "name": t.tool_name, "status": t.status} for t in tasks]}
