"""Initial schema - Enterprise-grade foundation

Revision ID: 001_initial
Revises:
Create Date: 2024-01-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Organizations (Phase 10)
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('plan', sa.String(20), default='enterprise', nullable=False),
        sa.Column('max_devices', sa.Integer, default=1000),
        sa.Column('max_users', sa.Integer, default=100),
        sa.Column('settings', JSONB, default=dict),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Departments
    op.create_table(
        'departments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('organization_id', 'name', name='uq_org_dept_name'),
    )

    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('plan', sa.String(20), default='free', nullable=False),
        sa.Column('two_factor_enabled', sa.Boolean, default=False),
        sa.Column('two_factor_secret', sa.String(255), nullable=True),
        sa.Column('email_verified', sa.Boolean, default=False),
        sa.Column('email_verification_token', sa.String(255), nullable=True),
        sa.Column('password_reset_token', sa.String(255), nullable=True),
        sa.Column('password_reset_expires', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_admin', sa.Boolean, default=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Org Members (Phase 10)
    op.create_table(
        'org_members',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('department_id', sa.String(36), sa.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True),
        sa.Column('role', sa.String(20), default='technician', nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('organization_id', 'user_id', name='uq_org_user'),
    )

    # Devices (Phase 1-2, 5)
    op.create_table(
        'devices',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('device_fingerprint', sa.String(128), unique=True, nullable=False, index=True),
        sa.Column('device_certificate', sa.Text, nullable=True),
        sa.Column('device_token', sa.String(500), unique=True, nullable=False),
        sa.Column('device_token_expires', sa.DateTime(timezone=True), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('hostname', sa.String(255), nullable=True),
        sa.Column('status', sa.String(20), default='offline'),
        sa.Column('windows_version', sa.String(100), nullable=True),
        sa.Column('windows_build', sa.String(50), nullable=True),
        sa.Column('agent_version', sa.String(50), nullable=True),
        sa.Column('cpu_info', sa.String(255), nullable=True),
        sa.Column('ram_total_gb', sa.Float, nullable=True),
        sa.Column('gpu_info', sa.String(255), nullable=True),
        sa.Column('disk_total_gb', sa.Float, nullable=True),
        sa.Column('disk_used_gb', sa.Float, nullable=True),
        sa.Column('tags', JSONB, default=list),
        sa.Column('uptime_seconds', sa.Integer, default=0),
        sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_heartbeat', sa.DateTime(timezone=True), nullable=True),
        sa.Column('auto_update', sa.Boolean, default=True),
        sa.Column('pending_update_version', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_devices_user_status', 'devices', ['user_id', 'status'])
    op.create_index('ix_devices_org_status', 'devices', ['organization_id', 'status'])

    # Device Sessions
    op.create_table(
        'device_sessions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('device_id', sa.String(36), sa.ForeignKey('devices.id', ondelete='CASCADE'), nullable=False),
        sa.Column('websocket_id', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('connected_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('disconnected_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Pair Codes
    op.create_table(
        'pair_codes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('code', sa.String(32), unique=True, nullable=False, index=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean, default=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Tool Definitions (Phase 3)
    op.create_table(
        'tool_definitions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('version', sa.String(20), default='1.0.0'),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('input_schema', JSONB, nullable=False),
        sa.Column('output_schema', JSONB, nullable=False),
        sa.Column('requires_approval', sa.Boolean, default=False),
        sa.Column('risk_level', sa.String(20), default='low'),
        sa.Column('allowed_on_plans', JSONB, default=list),
        sa.Column('examples', JSONB, default=list),
        sa.Column('documentation', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Schedules (Phase 9)
    op.create_table(
        'schedules',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('device_id', sa.String(36), sa.ForeignKey('devices.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('schedule_type', sa.String(20), nullable=False),
        sa.Column('cron_expression', sa.String(100), nullable=True),
        sa.Column('time_of_day', sa.String(5), nullable=True),
        sa.Column('day_of_week', sa.Integer, nullable=True),
        sa.Column('day_of_month', sa.Integer, nullable=True),
        sa.Column('commands', JSONB, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('last_run', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_run', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Commands (Phase 3-4)
    op.create_table(
        'commands',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('device_id', sa.String(36), sa.ForeignKey('devices.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tool_name', sa.String(100), nullable=False, index=True),
        sa.Column('tool_version', sa.String(20), default='1.0.0'),
        sa.Column('status', sa.String(20), default='queued', nullable=False),
        sa.Column('priority', sa.String(20), default='normal'),
        sa.Column('parameters', JSONB, nullable=False, default=dict),
        sa.Column('result', JSONB, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('error_code', sa.String(50), nullable=True),
        sa.Column('progress', sa.Integer, default=0),
        sa.Column('logs', JSONB, default=list),
        sa.Column('queued_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('requires_approval', sa.Boolean, default=False),
        sa.Column('approved_by', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('nonce', sa.String(64), unique=True, nullable=False, index=True),
        sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=True),
        sa.Column('schedule_id', sa.String(36), sa.ForeignKey('schedules.id', ondelete='SET NULL'), nullable=True),
        sa.Column('timeout_seconds', sa.Integer, default=300),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_commands_device_status', 'commands', ['device_id', 'status'])
    op.create_index('ix_commands_user_created', 'commands', ['user_id', 'created_at'])

    # Notifications
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('read', sa.Boolean, default=False),
        sa.Column('action_url', sa.String(500), nullable=True),
        sa.Column('metadata', JSONB, default=dict),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Subscriptions
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('subscription_id', sa.String(255), unique=True, nullable=True),
        sa.Column('customer_id', sa.String(255), nullable=True),
        sa.Column('plan', sa.String(20), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Payments
    op.create_table(
        'payments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('payment_id', sa.String(255), unique=True, nullable=True),
        sa.Column('amount', sa.Integer, nullable=False),
        sa.Column('currency', sa.String(3), default='usd'),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Settings
    op.create_table(
        'settings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('theme', sa.String(20), default='dark'),
        sa.Column('language', sa.String(10), default='en'),
        sa.Column('timezone', sa.String(50), default='UTC'),
        sa.Column('ai_model', sa.String(50), default='gpt-4'),
        sa.Column('notifications_email', sa.Boolean, default=True),
        sa.Column('notifications_browser', sa.Boolean, default=True),
        sa.Column('notifications_task', sa.Boolean, default=True),
        sa.Column('notifications_device', sa.Boolean, default=True),
        sa.Column('notifications_update', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Audit Logs (Phase 5)
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('device_id', sa.String(36), sa.ForeignKey('devices.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource', sa.String(100), nullable=False),
        sa.Column('resource_id', sa.String(36), nullable=True),
        sa.Column('details', JSONB, nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('success', sa.Boolean, default=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_audit_logs_user_time', 'audit_logs', ['user_id', 'timestamp'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action', 'timestamp'])

    # API Keys
    op.create_table(
        'api_keys',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('key_hash', sa.String(255), unique=True, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('last_used', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Agent Updates (Phase 6)
    op.create_table(
        'agent_updates',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('version', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('release_notes', sa.Text, nullable=True),
        sa.Column('windows_x64_url', sa.String(500), nullable=False),
        sa.Column('windows_arm64_url', sa.String(500), nullable=True),
        sa.Column('sha256_hash', sa.String(64), nullable=False),
        sa.Column('signature', sa.Text, nullable=False),
        sa.Column('is_mandatory', sa.Boolean, default=False),
        sa.Column('is_beta', sa.Boolean, default=False),
        sa.Column('released_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('download_count', sa.Integer, default=0),
        sa.Column('install_count', sa.Integer, default=0),
    )

    # Terminal Sessions (Phase 7)
    op.create_table(
        'terminal_sessions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('device_id', sa.String(36), sa.ForeignKey('devices.id', ondelete='CASCADE'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('recording_enabled', sa.Boolean, default=False),
        sa.Column('recording_path', sa.String(500), nullable=True),
        sa.Column('commands_executed', sa.Integer, default=0),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('terminal_sessions')
    op.drop_table('agent_updates')
    op.drop_table('api_keys')
    op.drop_index('ix_audit_logs_action', 'audit_logs')
    op.drop_index('ix_audit_logs_user_time', 'audit_logs')
    op.drop_table('audit_logs')
    op.drop_table('settings')
    op.drop_table('payments')
    op.drop_table('subscriptions')
    op.drop_table('notifications')
    op.drop_index('ix_commands_user_created', 'commands')
    op.drop_index('ix_commands_device_status', 'commands')
    op.drop_table('commands')
    op.drop_table('schedules')
    op.drop_table('tool_definitions')
    op.drop_table('pair_codes')
    op.drop_table('device_sessions')
    op.drop_index('ix_devices_org_status', 'devices')
    op.drop_index('ix_devices_user_status', 'devices')
    op.drop_table('devices')
    op.drop_table('org_members')
    op.drop_table('users')
    op.drop_table('departments')
    op.drop_table('organizations')
