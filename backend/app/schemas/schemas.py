from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PlanType(str, Enum):
    free = "free"
    pro = "pro"
    business = "business"
    enterprise = "enterprise"


class DeviceStatus(str, Enum):
    online = "online"
    offline = "offline"
    connecting = "connecting"


class TaskStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"
    paused = "paused"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    plan: PlanType
    two_factor_enabled: bool
    email_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    password: str = Field(min_length=8, max_length=128)


class TwoFactorVerify(BaseModel):
    code: str


class DeviceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class DevicePair(BaseModel):
    pair_code: str


class DeviceUpdate(BaseModel):
    name: Optional[str] = None


class DeviceResponse(BaseModel):
    id: str
    name: str
    status: DeviceStatus
    windows_version: Optional[str] = None
    agent_version: Optional[str] = None
    cpu: Optional[str] = None
    ram: Optional[str] = None
    gpu: Optional[str] = None
    disk_total: Optional[int] = None
    disk_used: Optional[int] = None
    uptime: int = 0
    last_seen: Optional[datetime] = None
    created_at: datetime
    group_id: Optional[str] = None

    model_config = {"from_attributes": True}


class DeviceGroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    group_type: str = "custom"
    color: str = "#6366f1"


class DeviceGroupResponse(BaseModel):
    id: str
    name: str
    group_type: str
    color: str
    device_count: int = 0

    model_config = {"from_attributes": True}


class TaskCreate(BaseModel):
    device_id: str
    tool_name: str
    parameters: Optional[dict] = None


class TaskResponse(BaseModel):
    id: str
    device_id: str
    name: str
    tool_name: str
    status: TaskStatus
    progress: int = 0
    result: Optional[dict] = None
    error_message: Optional[str] = None
    logs: List[str] = []
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    device_id: Optional[str] = None
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    message: str
    tool_calls: List[dict] = []
    task_id: Optional[str] = None


class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    read: bool
    action_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SettingsUpdate(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    ai_model: Optional[str] = None
    notifications_email: Optional[bool] = None
    notifications_browser: Optional[bool] = None
    notifications_task: Optional[bool] = None
    notifications_device: Optional[bool] = None
    notifications_update: Optional[bool] = None


class SettingsResponse(BaseModel):
    theme: str
    language: str
    timezone: str
    ai_model: str
    notifications_email: bool
    notifications_browser: bool
    notifications_task: bool
    notifications_device: bool
    notifications_update: bool

    model_config = {"from_attributes": True}


class CheckoutRequest(BaseModel):
    plan: PlanType


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str


class SubscriptionResponse(BaseModel):
    plan: PlanType
    status: str
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False


class AdminUserResponse(BaseModel):
    id: str
    email: str
    name: str
    plan: PlanType
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginationParams(BaseModel):
    page: int = 1
    per_page: int = 20
