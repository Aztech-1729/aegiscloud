"""API v1 Router — Enterprise Grade"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    devices,
    commands,
    tools,
    ai,
    notifications,
    settings,
    websocket,
    schedules,
    updates,
    organizations,
    audit,
    skills,
    policies,
    plugins,
    memory,
    events,
    certificates,
    oauth,
)

api_router = APIRouter()

# Authentication
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(oauth.router, prefix="/auth", tags=["OAuth Authentication"])

# Device Management (Phase 1-2)
api_router.include_router(devices.router, prefix="/devices", tags=["Devices"])

# Command System (Phase 3-4)
api_router.include_router(commands.router, prefix="/commands", tags=["Commands"])
api_router.include_router(tools.router, prefix="/tools", tags=["Tool Registry"])

# AI Assistant (Phase 4)
api_router.include_router(ai.router, prefix="/ai", tags=["AI Assistant"])

# File Management (Phase 8)

# Notifications
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

# Settings
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])

# Admin Panel

# History & Audit (Phase 5)
api_router.include_router(audit.router, prefix="/audit", tags=["Audit Logs"])

# Scheduler (Phase 9)
api_router.include_router(schedules.router, prefix="/schedules", tags=["Scheduler"])

# Auto-Updates (Phase 6)
api_router.include_router(updates.router, prefix="/updates", tags=["Agent Updates"])

# Organizations (Phase 10)
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])

# Skills (Multi-step tasks)
api_router.include_router(skills.router, prefix="/skills", tags=["Skills"])

# Policies (Automated rules)
api_router.include_router(policies.router, prefix="/policies", tags=["Policies"])

# Plugins (Extensible tools)
api_router.include_router(plugins.router, prefix="/plugins", tags=["Plugins"])

# Device Memory (AI context)
api_router.include_router(memory.router, prefix="/memory", tags=["Memory"])

# Events (Real-time stream)
api_router.include_router(events.router, prefix="/events", tags=["Events"])

# Certificates (mTLS)
api_router.include_router(certificates.router, prefix="/certificates", tags=["Certificates"])

# WebSocket (Real-time)
api_router.include_router(websocket.router, tags=["WebSocket"])
