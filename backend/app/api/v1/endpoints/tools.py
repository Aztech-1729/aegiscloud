"""Phase 3: Tool Registry endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.models import User
from app.api.deps.auth import get_current_user
from app.services.tool_registry import tool_registry

router = APIRouter()


@router.get("")
async def list_tools(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """List all approved tools with their schemas.
    
    Phase 3: Returns tool definitions with strict input/output schemas.
    Filtered by user's plan level.
    """
    tools = tool_registry.list_tools(
        category=category,
        plan=current_user.plan.value,
    )
    return {
        "tools": [
            {
                "name": t["name"],
                "version": t.get("version", "1.0.0"),
                "description": t["description"],
                "category": t["category"],
                "input_schema": t["input_schema"],
                "output_schema": t["output_schema"],
                "requires_approval": t.get("requires_approval", False),
                "risk_level": t.get("risk_level", "low"),
                "examples": t.get("examples", []),
            }
            for t in tools
        ],
        "total": len(tools),
    }


@router.get("/categories")
async def list_categories():
    """List all tool categories."""
    tools = tool_registry.list_tools()
    categories = sorted(set(t["category"] for t in tools))
    return {
        "categories": [
            {
                "name": cat,
                "count": len([t for t in tools if t["category"] == cat]),
            }
            for cat in categories
        ]
    }


@router.get("/{tool_name}")
async def get_tool(
    tool_name: str,
    current_user: User = Depends(get_current_user),
):
    """Get detailed tool definition."""
    tool = tool_registry.get_tool(tool_name)
    if not tool:
        return {"error": "Tool not found"}

    return {
        "name": tool["name"],
        "version": tool.get("version", "1.0.0"),
        "description": tool["description"],
        "category": tool["category"],
        "input_schema": tool["input_schema"],
        "output_schema": tool["output_schema"],
        "requires_approval": tool.get("requires_approval", False),
        "risk_level": tool.get("risk_level", "low"),
        "allowed_on_plans": tool.get("allowed_on_plans", []),
        "examples": tool.get("examples", []),
        "documentation": tool.get("documentation"),
        "available_on_current_plan": tool_registry.is_allowed_on_plan(tool_name, current_user.plan.value),
    }


@router.post("/{tool_name}/validate")
async def validate_tool_parameters(
    tool_name: str,
    parameters: dict,
    current_user: User = Depends(get_current_user),
):
    """Validate parameters against a tool's schema (dry run)."""
    try:
        validated = tool_registry.validate_parameters(tool_name, parameters)
        return {
            "valid": True,
            "validated_parameters": validated,
            "requires_approval": tool_registry.requires_approval(tool_name),
            "risk_level": tool_registry.get_risk_level(tool_name),
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
        }
