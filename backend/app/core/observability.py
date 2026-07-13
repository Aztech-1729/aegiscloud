"""Observability — OpenTelemetry metrics, traces, and logs.

Production systems need visibility into:
- Request latency
- Error rates
- Command execution times
- WebSocket connection counts
- Agent heartbeat frequency
- Memory usage
- CPU usage

This module provides structured observability for the entire platform.
"""
from datetime import datetime, timezone
from typing import Optional
import time
import json

from app.core.logging import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """Collects and exposes platform metrics."""

    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "requests_by_endpoint": {},
            "errors_total": 0,
            "commands_executed": 0,
            "commands_by_status": {},
            "agents_connected": 0,
            "agents_heartbeat_count": 0,
            "websocket_connections": 0,
            "request_latency_ms": [],
        }

    def record_request(self, endpoint: str, latency_ms: float, success: bool = True):
        """Record an API request."""
        self.metrics["requests_total"] += 1
        self.metrics["requests_by_endpoint"][endpoint] = (
            self.metrics["requests_by_endpoint"].get(endpoint, 0) + 1
        )
        self.metrics["request_latency_ms"].append(latency_ms)

        # Keep only last 1000 latency measurements
        if len(self.metrics["request_latency_ms"]) > 1000:
            self.metrics["request_latency_ms"] = self.metrics["request_latency_ms"][-1000:]

        if not success:
            self.metrics["errors_total"] += 1

    def record_command(self, status: str):
        """Record a command execution."""
        self.metrics["commands_executed"] += 1
        self.metrics["commands_by_status"][status] = (
            self.metrics["commands_by_status"].get(status, 0) + 1
        )

    def record_agent_connection(self, connected: bool):
        """Record agent connection/disconnection."""
        if connected:
            self.metrics["agents_connected"] += 1
        else:
            self.metrics["agents_connected"] = max(0, self.metrics["agents_connected"] - 1)

    def record_heartbeat(self):
        """Record agent heartbeat."""
        self.metrics["agents_heartbeat_count"] += 1

    def record_websocket_connection(self, connected: bool):
        """Record WebSocket connection."""
        if connected:
            self.metrics["websocket_connections"] += 1
        else:
            self.metrics["websocket_connections"] = max(0, self.metrics["websocket_connections"] - 1)

    def get_metrics(self) -> dict:
        """Get current metrics snapshot."""
        latencies = self.metrics["request_latency_ms"]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0
        p99_latency = sorted(latencies)[int(len(latencies) * 0.99)] if latencies else 0

        return {
            **self.metrics,
            "avg_latency_ms": round(avg_latency, 2),
            "p95_latency_ms": round(p95_latency, 2),
            "p99_latency_ms": round(p99_latency, 2),
            "error_rate": (
                self.metrics["errors_total"] / self.metrics["requests_total"]
                if self.metrics["requests_total"] > 0
                else 0
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


class TracingContext:
    """Distributed tracing context for request flow tracking."""

    def __init__(self, trace_id: str, span_id: str, parent_span_id: Optional[str] = None):
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.start_time = time.time()
        self.attributes = {}

    def set_attribute(self, key: str, value: any):
        """Set a span attribute."""
        self.attributes[key] = value

    def end_span(self, status: str = "ok"):
        """End the span and log it."""
        duration_ms = (time.time() - self.start_time) * 1000
        logger.info(
            "trace_span",
            trace_id=self.trace_id,
            span_id=self.span_id,
            parent_span_id=self.parent_span_id,
            duration_ms=round(duration_ms, 2),
            status=status,
            attributes=self.attributes,
        )


class HealthChecker:
    """Health check system for platform components."""

    def __init__(self, db_session_factory, redis_client):
        self.db_session_factory = db_session_factory
        self.redis_client = redis_client

    async def check_health(self) -> dict:
        """Check health of all platform components."""
        checks = {}

        # Database check
        try:
            async for session in self.db_session_factory():
                await session.execute("SELECT 1")
                checks["database"] = {"status": "healthy", "latency_ms": 0}
                break
        except Exception as e:
            checks["database"] = {"status": "unhealthy", "error": str(e)}

        # Redis check
        try:
            await self.redis_client.ping()
            checks["redis"] = {"status": "healthy", "latency_ms": 0}
        except Exception as e:
            checks["redis"] = {"status": "unhealthy", "error": str(e)}

        # Overall status
        all_healthy = all(check["status"] == "healthy" for check in checks.values())

        return {
            "status": "healthy" if all_healthy else "degraded",
            "checks": checks,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global instances
metrics = MetricsCollector()
health_checker: Optional[HealthChecker] = None


def init_observability(db_session_factory, redis_client):
    """Initialize observability components."""
    global health_checker
    health_checker = HealthChecker(db_session_factory, redis_client)
    logger.info("observability_initialized")
