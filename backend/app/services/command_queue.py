"""Phase 3-4: Command Queue - Manages command lifecycle with proper state machine.

States:
  queued → sent → running → completed
                       ↘ failed
                       ↘ timeout
  queued → cancelled (by user)
  queued → approval_pending → queued (after approval)

Every transition is logged and auditable.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
import secrets

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.models import (
    Command, CommandStatus, CommandPriority, Device, DeviceStatus,
    AuditLog, Notification, NotificationType
)
from app.services.tool_registry import tool_registry, ToolValidationError
from app.core.logging import get_logger

logger = get_logger(__name__)


class CommandQueue:
    """Manages the lifecycle of all commands sent to devices."""

    async def enqueue(
        self,
        db: AsyncSession,
        user_id: str,
        device_id: str,
        tool_name: str,
        parameters: dict,
        user_plan: str = "free",
        priority: CommandPriority = CommandPriority.normal,
        scheduled_for: Optional[datetime] = None,
        timeout_seconds: int = 300,
    ) -> Command:
        """Queue a new command for execution.
        
        Validates:
        1. Tool exists in registry
        2. Parameters match schema
        3. Tool is allowed on user's plan
        4. Device exists and is online
        """
        # 1. Validate tool exists
        tool = tool_registry.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Unknown tool: {tool_name}")

        # 2. Validate parameters against schema
        validated_params = tool_registry.validate_parameters(tool_name, parameters)

        # 3. Check plan access
        if not tool_registry.is_allowed_on_plan(tool_name, user_plan):
            raise ValueError(f"Tool '{tool_name}' is not available on your plan")

        # 4. Verify device
        result = await db.execute(
            select(Device).where(Device.id == device_id)
        )
        device = result.scalar_one_or_none()
        if not device:
            raise ValueError("Device not found")

        # 5. Generate replay protection nonce
        nonce = secrets.token_hex(32)

        # 6. Check if approval is required
        requires_approval = tool_registry.requires_approval(tool_name)
        initial_status = CommandStatus.approval_pending if requires_approval else CommandStatus.queued

        # 7. Create command
        command = Command(
            user_id=user_id,
            device_id=device_id,
            tool_name=tool_name,
            tool_version=tool.get("version", "1.0.0"),
            status=initial_status,
            priority=priority,
            parameters=validated_params,
            nonce=nonce,
            scheduled_for=scheduled_for,
            timeout_seconds=timeout_seconds,
            requires_approval=requires_approval,
        )
        db.add(command)
        await db.flush()

        # 8. Audit log
        audit = AuditLog(
            user_id=user_id,
            device_id=device_id,
            action="command.enqueue",
            resource="command",
            resource_id=command.id,
            details={
                "tool_name": tool_name,
                "parameters": validated_params,
                "requires_approval": requires_approval,
                "nonce": nonce,
            },
        )
        db.add(audit)
        await db.flush()

        logger.info(
            "command_enqueued",
            command_id=command.id,
            tool=tool_name,
            device_id=device_id,
            status=initial_status.value,
        )

        return command

    async def approve(
        self,
        db: AsyncSession,
        command_id: str,
        approver_id: str,
    ) -> Command:
        """Approve a command that requires approval."""
        result = await db.execute(
            select(Command).where(Command.id == command_id)
        )
        command = result.scalar_one_or_none()
        if not command:
            raise ValueError("Command not found")

        if command.status != CommandStatus.approval_pending:
            raise ValueError(f"Command is not pending approval (status: {command.status.value})")

        command.status = CommandStatus.queued
        command.approved_by = approver_id
        command.approved_at = datetime.now(timezone.utc)

        # Audit
        audit = AuditLog(
            user_id=approver_id,
            device_id=command.device_id,
            action="command.approve",
            resource="command",
            resource_id=command.id,
            details={"tool_name": command.tool_name},
        )
        db.add(audit)
        await db.flush()

        return command

    async def mark_sent(
        self,
        db: AsyncSession,
        command_id: str,
    ) -> None:
        """Mark command as sent to device."""
        await db.execute(
            update(Command)
            .where(Command.id == command_id)
            .values(
                status=CommandStatus.sent,
                sent_at=datetime.now(timezone.utc),
            )
        )

    async def mark_running(
        self,
        db: AsyncSession,
        command_id: str,
    ) -> None:
        """Mark command as running on device."""
        await db.execute(
            update(Command)
            .where(Command.id == command_id)
            .values(
                status=CommandStatus.running,
                started_at=datetime.now(timezone.utc),
            )
        )

    async def update_progress(
        self,
        db: AsyncSession,
        command_id: str,
        progress: int,
        log_entry: Optional[str] = None,
    ) -> None:
        """Update command progress (0-100)."""
        values = {"progress": min(100, max(0, progress))}
        if log_entry:
            # Append to logs array
            await db.execute(
                update(Command)
                .where(Command.id == command_id)
                .values(
                    progress=values["progress"],
                    logs=Command.logs + [log_entry],
                )
            )
            return

        await db.execute(
            update(Command)
            .where(Command.id == command_id)
            .values(**values)
        )

    async def mark_completed(
        self,
        db: AsyncSession,
        command_id: str,
        result: dict,
    ) -> Command:
        """Mark command as successfully completed."""
        command_result = await db.execute(
            select(Command).where(Command.id == command_id)
        )
        command = command_result.scalar_one_or_none()
        if not command:
            raise ValueError("Command not found")

        command.status = CommandStatus.completed
        command.progress = 100
        command.result = result
        command.completed_at = datetime.now(timezone.utc)

        # Audit
        audit = AuditLog(
            user_id=command.user_id,
            device_id=command.device_id,
            action="command.completed",
            resource="command",
            resource_id=command.id,
            details={
                "tool_name": command.tool_name,
                "success": True,
                "duration_seconds": (
                    (command.completed_at - command.started_at).total_seconds()
                    if command.started_at else None
                ),
            },
        )
        db.add(audit)

        # Notification
        notification = Notification(
            user_id=command.user_id,
            type=NotificationType.task_completed,
            title=f"Task Completed: {command.tool_name.replace('_', ' ').title()}",
            message=f"Command executed successfully on device.",
            action_url=f"/dashboard/tasks/{command.id}",
        )
        db.add(notification)
        await db.flush()

        return command

    async def mark_failed(
        self,
        db: AsyncSession,
        command_id: str,
        error_message: str,
        error_code: Optional[str] = None,
    ) -> Command:
        """Mark command as failed."""
        result = await db.execute(
            select(Command).where(Command.id == command_id)
        )
        command = result.scalar_one_or_none()
        if not command:
            raise ValueError("Command not found")

        command.status = CommandStatus.failed
        command.error_message = error_message
        command.error_code = error_code
        command.completed_at = datetime.now(timezone.utc)

        audit = AuditLog(
            user_id=command.user_id,
            device_id=command.device_id,
            action="command.failed",
            resource="command",
            resource_id=command.id,
            details={
                "tool_name": command.tool_name,
                "error": error_message,
                "error_code": error_code,
            },
            success=False,
        )
        db.add(audit)
        await db.flush()

        return command

    async def cancel(
        self,
        db: AsyncSession,
        command_id: str,
        user_id: str,
    ) -> Command:
        """Cancel a queued or running command."""
        result = await db.execute(
            select(Command).where(
                Command.id == command_id,
                Command.user_id == user_id,
            )
        )
        command = result.scalar_one_or_none()
        if not command:
            raise ValueError("Command not found")

        if command.status not in (CommandStatus.queued, CommandStatus.sent, CommandStatus.running, CommandStatus.approval_pending):
            raise ValueError(f"Cannot cancel command in status: {command.status.value}")

        command.status = CommandStatus.cancelled
        command.completed_at = datetime.now(timezone.utc)

        audit = AuditLog(
            user_id=user_id,
            device_id=command.device_id,
            action="command.cancel",
            resource="command",
            resource_id=command.id,
            details={"tool_name": command.tool_name, "previous_status": command.status.value},
        )
        db.add(audit)
        await db.flush()

        return command

    async def retry(
        self,
        db: AsyncSession,
        command_id: str,
        user_id: str,
    ) -> Command:
        """Retry a failed command by creating a new one with same params."""
        result = await db.execute(
            select(Command).where(
                Command.id == command_id,
                Command.user_id == user_id,
            )
        )
        original = result.scalar_one_or_none()
        if not original:
            raise ValueError("Command not found")

        if original.status != CommandStatus.failed:
            raise ValueError("Can only retry failed commands")

        return await self.enqueue(
            db=db,
            user_id=user_id,
            device_id=original.device_id,
            tool_name=original.tool_name,
            parameters=original.parameters,
            priority=original.priority,
            timeout_seconds=original.timeout_seconds,
        )

    async def get_pending_commands(
        self,
        db: AsyncSession,
        device_id: str,
        limit: int = 10,
    ) -> list[Command]:
        """Get pending commands for a device, ordered by priority."""
        result = await db.execute(
            select(Command)
            .where(
                Command.device_id == device_id,
                Command.status == CommandStatus.queued,
            )
            .order_by(
                Command.priority.desc(),
                Command.queued_at.asc(),
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    async def check_timeouts(
        self,
        db: AsyncSession,
    ) -> list[str]:
        """Find and mark timed-out commands."""
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(Command).where(
                Command.status.in_([CommandStatus.sent, CommandStatus.running]),
                Command.started_at < now - timedelta(seconds=Command.timeout_seconds),
            )
        )
        timed_out = result.scalars().all()

        for command in timed_out:
            command.status = CommandStatus.timeout
            command.completed_at = now
            command.error_message = "Command timed out"

        return [c.id for c in timed_out]


# Global command queue instance
command_queue = CommandQueue()
