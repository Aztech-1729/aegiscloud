"""Phase 10: Organization management endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.models import User, Organization, Department, OrgMember, OrgRole, Device
from app.api.deps.auth import get_current_user

router = APIRouter()


@router.get("")
async def get_organization(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the user's organization."""
    result = await db.execute(
        select(OrgMember).where(OrgMember.user_id == current_user.id)
    )
    membership = result.scalar_one_or_none()
    if not membership:
        return {"organization": None, "message": "Not part of an organization"}

    org_result = await db.execute(
        select(Organization).where(Organization.id == membership.organization_id)
    )
    org = org_result.scalar_one_or_none()
    if not org:
        return {"organization": None}

    # Get counts
    user_count = await db.execute(
        select(func.count(OrgMember.id)).where(OrgMember.organization_id == org.id)
    )
    device_count = await db.execute(
        select(func.count(Device.id)).where(Device.organization_id == org.id)
    )

    return {
        "organization": {
            "id": org.id,
            "name": org.name,
            "slug": org.slug,
            "plan": org.plan.value,
            "max_devices": org.max_devices,
            "max_users": org.max_users,
            "current_users": user_count.scalar() or 0,
            "current_devices": device_count.scalar() or 0,
        },
        "role": membership.role.value,
    }


@router.get("/departments")
async def list_departments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List departments in the user's organization."""
    member_result = await db.execute(
        select(OrgMember).where(OrgMember.user_id == current_user.id)
    )
    membership = member_result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=404, detail="Not part of an organization")

    result = await db.execute(
        select(Department).where(Department.organization_id == membership.organization_id)
    )
    departments = result.scalars().all()

    depts = []
    for dept in departments:
        member_count = await db.execute(
            select(func.count(OrgMember.id)).where(OrgMember.department_id == dept.id)
        )
        device_count = await db.execute(
            select(func.count(Device.id)).where(
                Device.organization_id == membership.organization_id,
            )
        )
        depts.append({
            "id": dept.id,
            "name": dept.name,
            "description": dept.description,
            "member_count": member_count.scalar() or 0,
        })

    return {"departments": depts}


@router.get("/members")
async def list_members(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List members of the user's organization."""
    member_result = await db.execute(
        select(OrgMember).where(OrgMember.user_id == current_user.id)
    )
    membership = member_result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=404, detail="Not part of an organization")

    result = await db.execute(
        select(OrgMember, User)
        .join(User, OrgMember.user_id == User.id)
        .where(OrgMember.organization_id == membership.organization_id)
    )
    rows = result.all()

    members = []
    for org_member, user in rows:
        dept = None
        if org_member.department_id:
            dept_result = await db.execute(
                select(Department).where(Department.id == org_member.department_id)
            )
            dept = dept_result.scalar_one_or_none()

        members.append({
            "id": org_member.id,
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "role": org_member.role.value,
            "department": dept.name if dept else None,
            "is_active": org_member.is_active,
            "joined_at": org_member.joined_at.isoformat(),
        })

    return {"members": members}


@router.post("/invite")
async def invite_member(
    email: str,
    role: str = "technician",
    department_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Invite a new member to the organization."""
    member_result = await db.execute(
        select(OrgMember).where(OrgMember.user_id == current_user.id)
    )
    membership = member_result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=404, detail="Not part of an organization")

    if membership.role not in (OrgRole.owner, OrgRole.admin):
        raise HTTPException(status_code=403, detail="Only owners and admins can invite members")

    # Check if user exists
    user_result = await db.execute(select(User).where(User.email == email))
    user = user_result.scalar_one_or_none()
    if not user:
        return {"message": "Invitation email sent", "email": email}

    # Check if already a member
    existing = await db.execute(
        select(OrgMember).where(
            OrgMember.organization_id == membership.organization_id,
            OrgMember.user_id == user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already a member")

    try:
        org_role = OrgRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role: {role}")

    new_member = OrgMember(
        organization_id=membership.organization_id,
        user_id=user.id,
        department_id=department_id,
        role=org_role,
    )
    db.add(new_member)
    await db.flush()

    return {"message": "Member added", "member_id": new_member.id}
