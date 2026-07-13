"""Database models for Aegis Cloud - Enterprise Grade"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, Integer, Float, DateTime, Text, JSON,
    ForeignKey, Enum as SAEnum, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ============= ENUMS =============

class PlanType(str, enum.Enum):
    free = "free"
    pro = "pro"
    business = "business"
    enterprise = "enterprise"


class DeviceStatus(str, enum.Enum):
    online = "online"
    offline = "offline"
    connecting = "connecting"
    updating = "updating"


class CommandStatus(str, enum.Enum):
    """Command execution states with proper lifecycle"""
    queued = "queued"          # In queue, waiting for agent
    sent = "sent"              # Sent to agent, awaiting ack
    running = "running"        # Agent executing
    completed = "completed"    # Success
    failed = "failed"          # Error occurred
    cancelled = "cancelled"    # User cancelled
    timeout = "timeout"        # Agent didn't respond
    approval_pending = "approval_pending"  # Waiting for approval


class CommandPriority(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"
    critical = "critical"


class NotificationType(str, enum.Enum):
    task_completed = "task_completed"
    device_offline = "device_offline"
    device_online = "device_online"
    update_available = "update_available"
    security_alert = "security_alert"
    approval_required = "approval_required"
    scheduled_task = "scheduled_task"


class ScheduleType(str, enum.Enum):
    once = "once"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    cron = "cron"


class OrgRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    manager = "manager"
    technician = "technician"
    viewer = "viewer"


# ============= ENTERPRISE MODELS =============

class Organization(Base):
    """Phase 10: Enterprise organization support"""
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    plan = Column(SAEnum(PlanType), default=PlanType.enterprise, nullable=False)
    max_devices = Column(Integer, default=1000)
    max_users = Column(Integer, default=100)
    settings = Column(JSONB, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    departments = relationship("Department", back_populates="organization", cascade="all, delete-orphan")
    members = relationship("OrgMember", back_populates="organization", cascade="all, delete-orphan")
    devices = relationship("Device", back_populates="organization")


class Department(Base):
    """Phase 10: Organizational departments"""
    __tablename__ = "departments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    organization = relationship("Organization", back_populates="departments")
    members = relationship("OrgMember", back_populates="department")

    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_org_dept_name'),
    )


class OrgMember(Base):
    """Phase 10: Organization membership with roles"""
    __tablename__ = "org_members"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    role = Column(SAEnum(OrgRole), default=OrgRole.technician, nullable=False)
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime(timezone=True), default=utcnow)

    organization = relationship("Organization", back_populates="members")
    user = relationship("User")
    department = relationship("Department", back_populates="members")

    __table_args__ = (
        UniqueConstraint('organization_id', 'user_id', name='uq_org_user'),
    )


# ============= USER MODELS =============

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    plan = Column(SAEnum(PlanType), default=PlanType.free, nullable=False)
    
    # Security
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255), nullable=True)
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    devices = relationship("Device", back_populates="user", cascade="all, delete-orphan")
    commands = relationship("Command", back_populates="user")


# ============= DEVICE MODELS (Phase 1, 2, 5) =============

class Device(Base):
    """Phase 1-2: Enhanced device with proper identity and lifecycle"""
    __tablename__ = "devices"
    __table_args__ = (
        Index("ix_devices_user_status", "user_id", "status"),
        Index("ix_devices_org_status", "organization_id", "status"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    
    # Device identity (Phase 5: Separate device authentication)
    device_fingerprint = Column(String(128), unique=True, nullable=False, index=True)
    device_certificate = Column(Text, nullable=True)  # X.509 certificate
    device_token = Column(String(500), unique=True, nullable=False)
    device_token_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Device info
    name = Column(String(255), nullable=False)
    hostname = Column(String(255), nullable=True)
    status = Column(SAEnum(DeviceStatus), default=DeviceStatus.offline)
    
    # System info
    windows_version = Column(String(100), nullable=True)
    windows_build = Column(String(50), nullable=True)
    agent_version = Column(String(50), nullable=True)
    cpu_info = Column(String(255), nullable=True)
    ram_total_gb = Column(Float, nullable=True)
    gpu_info = Column(String(255), nullable=True)
    disk_total_gb = Column(Float, nullable=True)
    disk_used_gb = Column(Float, nullable=True)
    
    # Tags (Phase 2)
    tags = Column(JSONB, default=list)  # ["gaming", "work", "production"]
    
    # Status tracking
    uptime_seconds = Column(Integer, default=0)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    
    # Update management (Phase 6)
    auto_update = Column(Boolean, default=True)
    pending_update_version = Column(String(50), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="devices")
    organization = relationship("Organization", back_populates="devices")
    commands = relationship("Command", back_populates="device", cascade="all, delete-orphan")
    sessions = relationship("DeviceSession", back_populates="device", cascade="all, delete-orphan")


class DeviceSession(Base):
    """Active WebSocket sessions"""
    __tablename__ = "device_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    websocket_id = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    connected_at = Column(DateTime(timezone=True), default=utcnow)
    disconnected_at = Column(DateTime(timezone=True), nullable=True)

    device = relationship("Device", back_populates="sessions")


class PairCode(Base):
    """Secure device pairing with expiration"""
    __tablename__ = "pair_codes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(32), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)


# ============= COMMAND SYSTEM (Phase 3, 4) =============

class Command(Base):
    """Phase 3-4: Typed command execution with full lifecycle"""
    __tablename__ = "commands"
    __table_args__ = (
        Index("ix_commands_device_status", "device_id", "status"),
        Index("ix_commands_user_created", "user_id", "created_at"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    
    # Command identity
    tool_name = Column(String(100), nullable=False, index=True)
    tool_version = Column(String(20), default="1.0.0")
    
    # Execution
    status = Column(SAEnum(CommandStatus), default=CommandStatus.queued, nullable=False)
    priority = Column(SAEnum(CommandPriority), default=CommandPriority.normal)
    
    # Parameters (typed JSON)
    parameters = Column(JSONB, nullable=False, default=dict)
    
    # Results
    result = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    
    # Execution tracking
    progress = Column(Integer, default=0)  # 0-100
    logs = Column(JSONB, default=list)
    
    # Lifecycle timestamps
    queued_at = Column(DateTime(timezone=True), default=utcnow)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Security & audit
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Replay protection (Phase 5)
    nonce = Column(String(64), unique=True, nullable=False, index=True)
    
    # Scheduling (Phase 9)
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    schedule_id = Column(String(36), ForeignKey("schedules.id", ondelete="SET NULL"), nullable=True)
    
    # Timeout
    timeout_seconds = Column(Integer, default=300)
    
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="commands")
    device = relationship("Device", back_populates="commands")
    schedule = relationship("Schedule", back_populates="commands")


class ToolDefinition(Base):
    """Phase 3: Registry of approved tools with strict typing"""
    __tablename__ = "tool_definitions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False, index=True)
    version = Column(String(20), default="1.0.0")
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # system, process, file, etc.
    
    # JSON Schema for parameters
    input_schema = Column(JSONB, nullable=False)
    output_schema = Column(JSONB, nullable=False)
    
    # Security
    requires_approval = Column(Boolean, default=False)
    risk_level = Column(String(20), default="low")  # low, medium, high, critical
    allowed_on_plans = Column(JSONB, default=list)  # ["free", "pro", "business", "enterprise"]
    
    # Metadata
    examples = Column(JSONB, default=list)
    documentation = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


# ============= SCHEDULER (Phase 9) =============

class Schedule(Base):
    """Phase 9: Scheduled maintenance tasks"""
    __tablename__ = "schedules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Schedule configuration
    schedule_type = Column(SAEnum(ScheduleType), nullable=False)
    cron_expression = Column(String(100), nullable=True)  # For cron type
    time_of_day = Column(String(5), nullable=True)  # HH:MM
    day_of_week = Column(Integer, nullable=True)  # 0-6 for weekly
    day_of_month = Column(Integer, nullable=True)  # 1-31 for monthly
    
    # Commands to execute
    commands = Column(JSONB, nullable=False)  # List of tool_name + parameters
    
    # Status
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime(timezone=True), nullable=True)
    next_run = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    commands_list = relationship("Command", back_populates="schedule")


# ============= NOTIFICATIONS =============

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(SAEnum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    action_url = Column(String(500), nullable=True)
    meta_data = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), default=utcnow)


# ============= SUBSCRIPTIONS =============

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    subscription_id = Column(String(255), unique=True, nullable=True)
    customer_id = Column(String(255), nullable=True)
    plan = Column(SAEnum(PlanType), nullable=False)
    status = Column(String(50), nullable=False)
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    payment_id = Column(String(255), unique=True, nullable=True)
    amount = Column(Integer, nullable=False)
    currency = Column(String(3), default="usd")
    status = Column(String(50), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)


# ============= SETTINGS =============

class Setting(Base):
    __tablename__ = "settings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    theme = Column(String(20), default="dark")
    language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    ai_model = Column(String(50), default="gpt-4")
    notifications_email = Column(Boolean, default=True)
    notifications_browser = Column(Boolean, default=True)
    notifications_task = Column(Boolean, default=True)
    notifications_device = Column(Boolean, default=True)
    notifications_update = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


# ============= AUDIT LOGS (Phase 5) =============

class AuditLog(Base):
    """Phase 5: Comprehensive audit logging"""
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_user_time", "user_id", "timestamp"),
        Index("ix_audit_logs_action", "action", "timestamp"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)  # "command.execute", "device.pair", etc.
    resource = Column(String(100), nullable=False)
    resource_id = Column(String(36), nullable=True)
    details = Column(JSONB, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    success = Column(Boolean, default=True)
    timestamp = Column(DateTime(timezone=True), default=utcnow)


# ============= API KEYS =============

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)


# ============= UPDATES (Phase 6) =============

class AgentUpdate(Base):
    """Phase 6: Agent update management"""
    __tablename__ = "agent_updates"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    version = Column(String(50), unique=True, nullable=False, index=True)
    release_notes = Column(Text, nullable=True)
    
    # Download URLs
    windows_x64_url = Column(String(500), nullable=False)
    windows_arm64_url = Column(String(500), nullable=True)
    
    # Verification
    sha256_hash = Column(String(64), nullable=False)
    signature = Column(Text, nullable=False)  # Ed25519 signature
    
    # Release info
    is_mandatory = Column(Boolean, default=False)
    is_beta = Column(Boolean, default=False)
    released_at = Column(DateTime(timezone=True), default=utcnow)
    
    # Stats
    download_count = Column(Integer, default=0)
    install_count = Column(Integer, default=0)


# ============= REMOTE TERMINAL (Phase 7) =============

class TerminalSession(Base):
    """Phase 7: Secure remote terminal with recording"""
    __tablename__ = "terminal_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    
    # Session info
    started_at = Column(DateTime(timezone=True), default=utcnow)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Recording (opt-in)
    recording_enabled = Column(Boolean, default=False)
    recording_path = Column(String(500), nullable=True)
    
    # Commands executed
    commands_executed = Column(Integer, default=0)
    
    # Security
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)


# ============= NEW MODELS FOR ADVANCED FEATURES =============

class Event(Base):
    """Real-time event stream"""
    __tablename__ = "events"
    __table_args__ = (Index("ix_events_user_time", "user_id", "created_at"),)

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_type = Column(String(100), nullable=False, index=True)  # device.online, command.completed, etc.
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    data = Column(JSONB, nullable=False, default=dict)
    severity = Column(String(20), default="info")  # info, warning, error, critical
    created_at = Column(DateTime(timezone=True), default=utcnow)


class DeviceMemory(Base):
    """Persistent AI memory for each device"""
    __tablename__ = "device_memory"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, unique=True)
    system_profile = Column(JSONB, nullable=True)  # Hardware specs, OS info
    performance_history = Column(JSONB, nullable=True)  # Array of {timestamp, cpu, ram, gpu, disk, temp}
    issue_history = Column(JSONB, nullable=True)  # Array of {timestamp, issue, resolution, severity}
    installed_apps = Column(JSONB, nullable=True)  # Array of app info
    preferences = Column(JSONB, nullable=True)  # User preferences for this device
    recommendations = Column(JSONB, nullable=True)  # AI-generated recommendations
    memory_version = Column(Integer, default=1)  # Schema version for migrations
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class DeviceCertificate(Base):
    """X.509 certificates for device authentication (mTLS)"""
    __tablename__ = "device_certificates"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    certificate_pem = Column(Text, nullable=False)
    csr_pem = Column(Text, nullable=False)
    issued_at = Column(DateTime(timezone=True), default=utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    __table_args__ = (Index("ix_device_cert_active", "device_id", "is_active"),)


class Skill(Base):
    """Reusable multi-step task templates"""
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    skill_id = Column(String(100), unique=True, nullable=False, index=True)  # e.g., "gaming-optimization"
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    author = Column(String(255), nullable=False)
    version = Column(String(50), default="1.0.0")
    icon = Column(String(10), default="🔧")
    steps = Column(JSONB, nullable=False)  # Array of {tool, parameters, description}
    estimated_time = Column(String(50), nullable=True)
    risk_level = Column(String(20), default="low")
    installed_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    tags = Column(JSONB, default=list)
    is_builtin = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class SkillInstallation(Base):
    """Track which skills are installed by users"""
    __tablename__ = "skill_installations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    installed_at = Column(DateTime(timezone=True), default=utcnow)

    __table_args__ = (Index("ix_skill_install_user", "user_id", "skill_id", unique=True),)


class Plugin(Base):
    """Extensible tool plugins"""
    __tablename__ = "plugins"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    plugin_id = Column(String(100), unique=True, nullable=False, index=True)  # e.g., "gpu-control"
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    version = Column(String(50), default="1.0.0")
    author = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    icon = Column(String(10), default="🔌")
    tools = Column(JSONB, nullable=False)  # Array of tool definitions
    download_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    size_mb = Column(Float, default=0.0)
    requires_restart = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)


class PluginInstallation(Base):
    """Track which plugins are installed on devices"""
    __tablename__ = "plugin_installations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    plugin_id = Column(String(36), ForeignKey("plugins.id", ondelete="CASCADE"), nullable=False)
    version = Column(String(50), nullable=False)
    installed_at = Column(DateTime(timezone=True), default=utcnow)

    __table_args__ = (Index("ix_plugin_install", "user_id", "device_id", "plugin_id", unique=True),)


class Policy(Base):
    """Automated rules and policies"""
    __tablename__ = "policies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), nullable=True)  # null = applies to all
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    condition = Column(JSONB, nullable=False)  # {type, metric, operator, value, duration_minutes}
    actions = Column(JSONB, nullable=False)  # Array of {type, tool, parameters, message}
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime(timezone=True), nullable=True)
    trigger_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    __table_args__ = (Index("ix_policies_user_active", "user_id", "is_active"),)


class PolicyAction(Base):
    """Log of policy executions"""
    __tablename__ = "policy_actions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    policy_id = Column(String(36), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    condition_matched = Column(JSONB, nullable=False)
    actions_executed = Column(JSONB, nullable=False)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    triggered_at = Column(DateTime(timezone=True), default=utcnow)
