# Aegis Cloud Architecture

## Overview

Aegis Cloud is an enterprise-grade AI-powered device management platform that allows organizations to remotely manage Windows devices through a web dashboard and AI assistant.

## System Components

### 1. Frontend (Next.js 14)

**Technology Stack**:
- Next.js 14 with App Router
- React 18 with TypeScript
- Tailwind CSS for styling
- Zustand for state management
- React Hook Form + Zod for forms
- TanStack Query for server state

**Responsibilities**:
- User interface and interactions
- Real-time WebSocket updates
- Command palette (Ctrl+K)
- Responsive design (mobile, tablet, desktop)
- Dark/light/system themes

**Key Pages**:
- Landing page (marketing)
- Authentication (login, register, 2FA)
- Dashboard (device overview)
- Device management (list, detail, actions)
- AI assistant (chat interface)
- Task manager (command history)
- File explorer (remote files)
- Scheduler (automated tasks)
- Fleet policies (group management)
- Skills marketplace
- Plugin marketplace
- Billing and settings

### 2. Backend (FastAPI)

**Technology Stack**:
- FastAPI (async Python framework)
- PostgreSQL 16 (primary database)
- Redis 7 (cache, pub/sub, rate limiting)
- SQLAlchemy 2.0 (ORM)
- Pydantic v2 (validation)
- Celery (background tasks)

**Core Services**:

#### Authentication Service
- JWT token management
- Two-factor authentication (TOTP)
- OAuth integration (Google, GitHub)
- Session management
- Password reset flows

#### Device Management Service
- Device registration and pairing
- Device status tracking (online/offline)
- Device metadata (OS, CPU, RAM, GPU, disk)
- Device groups and tags
- Certificate management (mTLS)

#### Command Queue Service
- Command lifecycle management
- Priority-based queuing
- Approval workflow for high-risk commands
- Replay protection (nonces)
- Result tracking and audit logs

#### Tool Registry
- 29 approved tools (system, process, file, network, security)
- JSON Schema validation for inputs/outputs
- Risk level classification (low/medium/high/critical)
- Plan-based access control
- Parameter validation

#### AI Pipeline
- Multi-step reasoning (Planner → Executor → Verifier)
- Intent analysis
- Conditional execution
- Result verification
- Memory persistence
- Recommendation generation

#### Skills Engine
- 8 built-in skills (gaming optimization, security audit, etc.)
- Multi-step task execution
- Dependency-aware ordering
- Error handling and retry

#### Policy Engine
- Fleet-wide policies
- Scheduled execution (cron)
- Threshold alerts
- Auto-remediation
- Compliance checks

#### Event Bus
- Redis pub/sub for real-time events
- 30+ event types
- Event persistence for audit
- Reactive architecture

#### Plugin SDK
- Plugin manifest schema
- Security review process
- CLI commands (init/build/test/publish)
- Permission system

### 3. Windows Agent (Rust)

**Technology Stack**:
- Rust (memory-safe, high-performance)
- Windows Service API
- tokio (async runtime)
- tungstenite (WebSocket client)
- ed25519-dalek (signature verification)
- TPM support (optional hardware security)

**Responsibilities**:
- Run as Windows Service (auto-start, crash recovery)
- Execute approved tools (system_info, cpu_usage, etc.)
- Real-time WebSocket communication
- Secure update mechanism
- Network monitoring and adaptation
- Crash recovery (persistent state)

**Key Features**:
- **Zero-Touch Install**: Download → Install → Done
- **Crash Recovery**: Survives reboots, sleep, network loss
- **Network Adaptation**: Detects VPN/WiFi changes
- **Signature Verification**: Ed25519 for update validation
- **Minimal Resource Usage**: <10MB RAM, <1% CPU

## Data Flow

### Command Execution Flow

```
User (Web)
  ↓
[1] POST /api/v1/commands
  ↓
Backend validates:
  - Tool exists in registry
  - Parameters match schema
  - User has plan access
  - Device is online
  ↓
[2] Command queued in PostgreSQL
  ↓
[3] Event published to Redis
  ↓
Agent receives via WebSocket
  ↓
[4] Agent executes tool
  ↓
[5] Agent sends result
  ↓
Backend updates command status
  ↓
[6] WebSocket notification to user
  ↓
User sees completion
```

### Device Connection Flow

```
Agent starts
  ↓
[1] Generate device fingerprint
  ↓
[2] Request enrollment (pair code)
  ↓
Backend creates device record
  ↓
[3] Issue device certificate
  ↓
Agent stores certificate
  ↓
[4] Connect via WebSocket (WSS + mTLS)
  ↓
[5] Send heartbeat every 30s
  ↓
Backend tracks status
  ↓
Dashboard shows device online
```

### AI Pipeline Flow

```
User message: "My PC is slow"
  ↓
[1] Intent Analysis
  - Detects: performance diagnosis
  ↓
[2] Planner generates execution plan
  - Steps: [cpu_usage, ram_usage, disk_usage, list_processes]
  ↓
[3] Executor runs tools in sequence
  - Each tool validated against registry
  - Commands queued and executed
  ↓
[4] Verifier analyzes results
  - CPU > 90%? → Finding: High CPU
  - RAM > 85%? → Finding: Memory pressure
  ↓
[5] Memory stores findings
  - For future context
  ↓
[6] AI generates response
  - "I found high CPU usage from Chrome..."
  - Recommendations: close apps, check startup
  ↓
User receives intelligent response
```

## Security Architecture

### Defense in Depth

```
Layer 1: Network
  - TLS 1.3 encryption
  - Firewall (only 443 exposed)
  - DDoS protection

Layer 2: Authentication
  - JWT with short expiration
  - Two-factor authentication
  - OAuth integration

Layer 3: Authorization
  - Role-based access control
  - Plan-based feature access
  - Device-level permissions

Layer 4: Application
  - Input validation (Pydantic)
  - Tool registry (no arbitrary commands)
  - Parameter validation (JSON Schema)

Layer 5: Data
  - Encryption at rest
  - Password hashing (bcrypt)
  - Audit logging

Layer 6: Agent
  - Code signing
  - Signature verification
  - TPM support
  - Sandboxed execution
```

### Zero Trust Principles

1. **Never trust, always verify**
   - Every API call authenticated
   - Every command validated
   - Every tool checked against registry

2. **Least privilege**
   - Devices can only execute approved tools
   - Users can only access their devices
   - Admins have minimal required permissions

3. **Assume breach**
   - Audit logs for all actions
   - Anomaly detection
   - Incident response plan

## Scalability Design

### Horizontal Scaling

**Backend**:
- Stateless FastAPI workers
- Load balancer (NGINX/AWS ALB)
- Auto-scaling based on CPU/memory
- PostgreSQL connection pooling

**Redis**:
- Redis Cluster for high availability
- Sharded by user_id
- Pub/sub across cluster

**PostgreSQL**:
- Read replicas for queries
- Connection pooling (PgBouncer)
- Partitioning by user_id

**WebSocket**:
- Multiple WebSocket servers
- Redis pub/sub for cross-server messaging
- Sticky sessions (optional)

### Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| API latency (P95) | <500ms | FastAPI + Redis cache |
| WebSocket latency | <100ms | Direct connection |
| Commands/sec | 10,000 | Async processing |
| Concurrent agents | 100,000 | Horizontal scaling |
| Database queries | <50ms | Indexed queries |

## Deployment Architecture

### Production Environment

```
┌─────────────────────────────────────────┐
│          Load Balancer (AWS ALB)         │
│         SSL termination, routing        │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────┐          ┌────▼────┐
│Backend │          │Backend  │
│Worker 1│          │Worker 2 │
└───┬────┘          └────┬────┘
    │                     │
    └──────────┬──────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────┐          ┌────▼────┐
│PostgreSQL│        │PostgreSQL│
│ Primary  │        │Replica  │
└──────────┘        └─────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────┐          ┌────▼────┐
│ Redis  │          │ Redis   │
│Cluster │          │Cluster  │
└────────┘          └─────────┘
```

### Infrastructure as Code

- **Terraform**: Cloud infrastructure
- **Helm**: Kubernetes deployments
- **Docker Compose**: Local development
- **GitHub Actions**: CI/CD pipeline

## Monitoring & Observability

### Metrics (Prometheus)

- Request count and latency
- Error rates
- WebSocket connections
- Agent count
- Command execution rate
- Database query time
- Redis memory usage

### Tracing (OpenTelemetry + Jaeger)

- Distributed traces across services
- Request flow visualization
- Performance bottleneck identification

### Logging (ELK Stack)

- Centralized logging
- Log aggregation
- Search and analysis
- Alerting on anomalies

### Dashboards (Grafana)

- Platform overview
- Agent health
- Command execution
- API performance
- Security metrics

## Disaster Recovery

### Backup Strategy

- **PostgreSQL**: Daily snapshots, WAL archiving
- **Redis**: RDB snapshots, AOF logging
- **Configuration**: Git repository (version controlled)
- **Agent binaries**: S3/GCS with versioning

### Recovery Time Objectives

| Component | RTO | RPO |
|-----------|-----|-----|
| Backend | 15 min | 5 min |
| Database | 1 hour | 1 hour |
| Redis | 30 min | 15 min |
| Full system | 2 hours | 1 hour |

### Failover

- **Multi-AZ deployment**: Automatic failover
- **Database replica**: Promoted on primary failure
- **Redis Sentinel**: Automatic master election
- **WebSocket reconnection**: Agents reconnect automatically

---

## Version History

- **v1.0** (2024-01-15): Initial architecture
- **v1.1** (2024-01-20): Added event bus
- **v1.2** (2024-02-01): Added fleet policies
- **v1.3** (2024-02-15): Added skills engine
- **v2.0** (2024-03-01): Production hardening
