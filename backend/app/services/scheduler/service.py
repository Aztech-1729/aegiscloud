"""Phase 9: Scheduler Service - Runs maintenance tasks on schedule.

Supports:
- One-time execution
- Daily at specific time
- Weekly on specific day
- Monthly on specific day
- Cron expressions

Each scheduled task creates Command entries in the queue.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.models import Schedule, ScheduleType, Command, CommandStatus
from app.services.command_queue import command_queue
from app.core.logging import get_logger

logger = get_logger(__name__)


class SchedulerService:
    """Manages scheduled maintenance tasks."""

    async def create_schedule(
        self,
        db: AsyncSession,
        user_id: str,
        device_id: str,
        name: str,
        schedule_type: ScheduleType,
        commands: list[dict],
        description: Optional[str] = None,
        cron_expression: Optional[str] = None,
        time_of_day: Optional[str] = None,
        day_of_week: Optional[int] = None,
        day_of_month: Optional[int] = None,
    ) -> Schedule:
        """Create a new scheduled maintenance task."""
        schedule = Schedule(
            user_id=user_id,
            device_id=device_id,
            name=name,
            description=description,
            schedule_type=schedule_type,
            commands=commands,
            cron_expression=cron_expression,
            time_of_day=time_of_day or "02:00",
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            next_run=self._calculate_next_run(schedule_type, time_of_day, day_of_week, day_of_month, cron_expression),
        )
        db.add(schedule)
        await db.flush()
        return schedule

    async def execute_scheduled(self, db: AsyncSession) -> list[str]:
        """Execute all schedules that are due. Called periodically."""
        now = datetime.now(timezone.utc)

        result = await db.execute(
            select(Schedule).where(
                Schedule.is_active == True,
                Schedule.next_run <= now,
            )
        )
        due_schedules = result.scalars().all()

        executed_ids = []
        for schedule in due_schedules:
            try:
                await self._execute_schedule(db, schedule)
                schedule.last_run = now
                schedule.next_run = self._calculate_next_run(
                    schedule.schedule_type,
                    schedule.time_of_day,
                    schedule.day_of_week,
                    schedule.day_of_month,
                    schedule.cron_expression,
                )
                executed_ids.append(schedule.id)
                logger.info("schedule_executed", schedule_id=schedule.id, name=schedule.name)
            except Exception as e:
                logger.error("schedule_failed", schedule_id=schedule.id, error=str(e))

        return executed_ids

    async def _execute_schedule(self, db: AsyncSession, schedule: Schedule) -> None:
        """Execute all commands in a schedule."""
        commands_data = schedule.commands
        if not isinstance(commands_data, list):
            return

        for cmd_data in commands_data:
            tool_name = cmd_data.get("tool_name")
            parameters = cmd_data.get("parameters", {})

            if not tool_name:
                continue

            try:
                await command_queue.enqueue(
                    db=db,
                    user_id=schedule.user_id,
                    device_id=schedule.device_id,
                    tool_name=tool_name,
                    parameters=parameters,
                    scheduled_for=datetime.now(timezone.utc),
                )
            except Exception as e:
                logger.error("schedule_command_failed", tool=tool_name, error=str(e))

    def _calculate_next_run(
        self,
        schedule_type: ScheduleType,
        time_of_day: Optional[str] = None,
        day_of_week: Optional[int] = None,
        day_of_month: Optional[int] = None,
        cron_expression: Optional[str] = None,
    ) -> datetime:
        """Calculate the next run time based on schedule configuration."""
        now = datetime.now(timezone.utc)
        time_parts = (time_of_day or "02:00").split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0

        if schedule_type == ScheduleType.once:
            return now + timedelta(hours=1)

        elif schedule_type == ScheduleType.daily:
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run

        elif schedule_type == ScheduleType.weekly:
            target_day = day_of_week or 0  # Default: Sunday
            days_ahead = target_day - now.weekday()
            if days_ahead < 0:
                days_ahead += 7
            next_run = (now + timedelta(days=days_ahead)).replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )
            if next_run <= now:
                next_run += timedelta(weeks=1)
            return next_run

        elif schedule_type == ScheduleType.monthly:
            target_day = day_of_month or 1
            next_month = now.replace(day=1) + timedelta(days=32)
            next_run = next_month.replace(
                day=min(target_day, 28),
                hour=hour, minute=minute, second=0, microsecond=0,
            )
            return next_run

        elif schedule_type == ScheduleType.cron:
            # Simple cron parser - default to daily
            return now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=1)

        return now + timedelta(days=1)


# Global scheduler instance
scheduler_service = SchedulerService()
