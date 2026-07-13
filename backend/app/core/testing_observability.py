"""Aegis Cloud — Observability & Testing Infrastructure

OpenTelemetry metrics, tracing, and comprehensive testing setup.
"""
import os

# ============= OPEN TELEMETRY CONFIG =============

OTEL_CONFIG = {
    "service_name": "aegis-cloud-backend",
    "service_version": "2.0.0",
    "exporters": {
        "prometheus": {
            "enabled": True,
            "port": 9090,
            "endpoint": "/metrics",
        },
        "jaeger": {
            "enabled": True,
            "endpoint": "http://localhost:14268/api/traces",
        },
        "otlp": {
            "enabled": False,
            "endpoint": "http://localhost:4317",
        },
    },
    "metrics": {
        "http_request_duration_seconds": {
            "type": "histogram",
            "labels": ["method", "endpoint", "status"],
        },
        "http_requests_total": {
            "type": "counter",
            "labels": ["method", "endpoint", "status"],
        },
        "websocket_connections_active": {
            "type": "gauge",
            "labels": [],
        },
        "agents_connected_total": {
            "type": "gauge",
            "labels": [],
        },
        "commands_executed_total": {
            "type": "counter",
            "labels": ["tool_name", "status"],
        },
        "command_duration_seconds": {
            "type": "histogram",
            "labels": ["tool_name"],
        },
        "database_query_duration_seconds": {
            "type": "histogram",
            "labels": ["operation"],
        },
        "redis_operations_total": {
            "type": "counter",
            "labels": ["operation"],
        },
        "events_published_total": {
            "type": "counter",
            "labels": ["event_type"],
        },
        "active_skills_total": {
            "type": "gauge",
            "labels": [],
        },
    },
}


# ============= PROMETHEUS CONFIG =============

PROMETHEUS_CONFIG = """
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'aegis-backend'
    static_configs:
      - targets: ['backend:9090']
    metrics_path: '/metrics'
    
  - job_name: 'aegis-postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
    
  - job_name: 'aegis-redis'
    static_configs:
      - targets: ['redis-exporter:9121']
    
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

rule_files:
  - 'alert_rules.yml'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
"""


# ============= ALERT RULES =============

ALERT_RULES = """
groups:
  - name: aegis_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status="5xx"}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 5% for 5 minutes"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API latency"
          description: "P95 latency is above 2 seconds"

      - alert: AgentsDisconnected
        expr: agents_connected_total < 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "No agents connected"
          description: "No agents have been connected for 10 minutes"

      - alert: DatabaseSlow
        expr: histogram_quantile(0.95, rate(database_query_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database queries are slow"
          description: "P95 query time is above 1 second"

      - alert: CommandQueueBacklog
        expr: commands_in_queue > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Command queue backlog"
          description: "More than 100 commands waiting in queue"

      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes / 1024 / 1024 / 1024 > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Backend using more than 2GB of RAM"
"""


# ============= GRAFANA DASHBOARD =============

GRAFANA_DASHBOARD = {
    "title": "Aegis Cloud — Platform Overview",
    "panels": [
        {
            "title": "Request Rate",
            "type": "graph",
            "targets": [
                {"expr": "rate(http_requests_total[5m])"}
            ],
        },
        {
            "title": "Request Latency (P95)",
            "type": "graph",
            "targets": [
                {"expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"}
            ],
        },
        {
            "title": "Connected Agents",
            "type": "stat",
            "targets": [
                {"expr": "agents_connected_total"}
            ],
        },
        {
            "title": "Commands Executed",
            "type": "graph",
            "targets": [
                {"expr": "rate(commands_executed_total[5m])"}
            ],
        },
        {
            "title": "Error Rate",
            "type": "graph",
            "targets": [
                {"expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m])"}
            ],
        },
        {
            "title": "WebSocket Connections",
            "type": "stat",
            "targets": [
                {"expr": "websocket_connections_active"}
            ],
        },
    ],
}


# ============= TEST INFRASTRUCTURE =============

LOAD_TEST_SCENARIOS = {
    "100_agents": {
        "description": "Simulate 100 agents connecting and sending heartbeats",
        "agents": 100,
        "duration_seconds": 300,
        "heartbeat_interval": 30,
        "commands_per_agent": 5,
    },
    "1000_agents": {
        "description": "Simulate 1000 agents with mixed load",
        "agents": 1000,
        "duration_seconds": 600,
        "heartbeat_interval": 30,
        "commands_per_agent": 10,
    },
    "10000_agents": {
        "description": "Stress test with 10K agents",
        "agents": 10000,
        "duration_seconds": 900,
        "heartbeat_interval": 30,
        "commands_per_agent": 3,
    },
    "command_flood": {
        "description": "Flood test — 1000 commands/second",
        "agents": 100,
        "duration_seconds": 60,
        "commands_per_second": 1000,
    },
    "websocket_burst": {
        "description": "10K WebSocket connections in 10 seconds",
        "connections": 10000,
        "burst_duration_seconds": 10,
        "hold_duration_seconds": 60,
    },
}

# ============= UNIT TEST PLAN =============

UNIT_TEST_PLAN = {
    "backend": {
        "test_files": [
            "tests/test_auth.py",
            "tests/test_devices.py",
            "tests/test_commands.py",
            "tests/test_tools.py",
            "tests/test_ai_pipeline.py",
            "tests/test_skills.py",
            "tests/test_policies.py",
            "tests/test_scheduler.py",
            "tests/test_event_bus.py",
            "tests/test_websocket.py",
        ],
        "coverage_target": 90,
    },
    "agent": {
        "test_files": [
            "tests/test_crash_recovery.rs",
            "tests/test_network_monitor.rs",
            "tests/test_command_queue.rs",
            "tests/test_tool_executor.rs",
            "tests/test_updater.rs",
            "tests/test_terminal.rs",
        ],
        "coverage_target": 85,
    },
    "frontend": {
        "test_files": [
            "__tests__/pages.test.tsx",
            "__tests__/components.test.tsx",
            "__tests__/stores.test.ts",
            "__tests__/api.test.ts",
        ],
        "coverage_target": 80,
    },
}


# ============= PENETRATION TEST PLAN =============

PEN_TEST_PLAN = {
    "authentication": [
        "JWT token forgery",
        "Token expiration bypass",
        "Refresh token replay",
        "Brute force login",
        "2FA bypass",
        "Session hijacking",
    ],
    "device_security": [
        "Device token extraction",
        "Certificate forgery",
        "Unauthorized device pairing",
        "WebSocket impersonation",
        "Command injection",
        "Replay attack on commands",
    ],
    "api_security": [
        "SQL injection",
        "Rate limit bypass",
        "IDOR (access other users' data)",
        "Mass assignment",
        "Path traversal in file operations",
        "Parameter tampering",
    ],
    "agent_security": [
        "Binary tampering",
        "Update signature bypass",
        "Privilege escalation",
        "Memory dump for secrets",
        "Log injection",
        "Denial of service",
    ],
    "network_security": [
        "MITM on WebSocket",
        "Certificate pinning bypass",
        "DNS rebinding",
        "DDoS simulation",
        "Port scanning",
    ],
}
