# Aegis Cloud — AI-Powered Endpoint Management Platform

An enterprise-grade SaaS platform for securely managing Windows endpoints from anywhere through a modern web dashboard. Users install a lightweight Windows Agent, pair it with their account, and manage their endpoints entirely from the browser.

**Built for MSPs, IT departments, power users, developers, small businesses, and enterprises.**

---

## What is Aegis Cloud?

Aegis Cloud is a comprehensive endpoint management platform that combines:
- **Remote device management** (like TeamViewer/AnyDesk)
- **AI-powered automation** (like ChatGPT for your infrastructure)
- **Enterprise endpoint control** (like Microsoft Intune)
- **Plugin ecosystem** (like VS Code extensions)
- **Real-time monitoring** (like Grafana/Datadog)

All controlled through natural language and a beautiful web interface.

---

## Key Features

### 🖥️ Endpoint Management
- **Device Discovery**: Auto-discover and pair Windows endpoints
- **Real-time Monitoring**: Live CPU, RAM, GPU, disk, network metrics
- **Remote Actions**: Restart, shutdown, wake-on-LAN, file management
- **Terminal Access**: Secure browser-based terminal with PTY
- **Fleet Management**: Manage thousands of devices with groups and policies

### 🤖 AI Assistant
- **Natural Language**: "Clean temp files", "Show large files", "Restart Explorer"
- **Tool Selection**: AI chooses from 29+ approved tools (no arbitrary commands)
- **Multi-step Reasoning**: Complex tasks broken into safe, auditable steps
- **Context-Aware**: Remembers device history and user preferences

### 🔧 Plugin Ecosystem
- **Extensible**: Build custom tools with our Rust SDK
- **Marketplace**: Install community and official plugins
- **Sandboxed**: All plugins run in secure isolation
- **Code-Signed**: Automatic signature verification

### 📅 Automation
- **Scheduled Tasks**: Daily/weekly/monthly maintenance
- **Policy Engine**: Automated responses to system events
- **Skills**: Pre-built multi-step workflows (Gaming Optimization, Security Audit, etc.)
- **Auto-Updates**: Silent agent updates with rollback

### 🔒 Enterprise Security
- **Zero Trust**: No direct shell access, only approved tools
- **mTLS**: Device certificates for authentication
- **Audit Logs**: Complete trail of all actions
- **RBAC**: Role-based access control (Owner, Admin, Manager, Technician, Viewer)
- **2FA**: Two-factor authentication with TOTP

### 📊 Observability
- **Live Dashboards**: Real-time metrics with Grafana
- **Event Streaming**: React to system events instantly
- **Alerting**: Prometheus alerts for anomalies
- **Tracing**: OpenTelemetry distributed tracing

---

## Architecture

```
Browser (Next.js 15 + React 19)
    ↓
FastAPI Backend (Python 3.13)
    ↓
Secure WebSocket (WSS + mTLS)
    ↓
Rust Windows Agent (Windows Service)
    ↓
Windows APIs / PowerShell / Registry / Processes / Services / Filesystem
    ↓
Plugin Runtime (Sandboxed Execution)
```

## Tech Stack

### Frontend
- **Next.js 15** with React 19 and TypeScript
- **Tailwind CSS** with custom design system
- **shadcn/ui** component library (Radix primitives)
- **Framer Motion** for animations
- **Zustand** for state management
- **TanStack Query** for data fetching
- **React Hook Form** + **Zod** for forms/validation
- **Recharts** for data visualization
- **xterm.js** for terminal emulation

### Backend
- **FastAPI** with async support
- **SQLAlchemy 2.0** with async sessions
- **PostgreSQL 16** database
- **Redis** for caching and pub/sub
- **WebSockets** for real-time communication
- **JWT** authentication with refresh tokens
- **Pydantic v2** for validation
- **Stripe** for billing integration
- **Celery** for background tasks
- **OpenTelemetry** for observability

### Windows Agent
- **Rust** for performance and safety
- Runs as a **Windows Service**
- **tokio** async runtime
- **tokio-tungstenite** for WebSocket
- **sysinfo** for system monitoring
- **libloading** for plugin execution
- **ed25519-dalek** for signature verification
- Auto-reconnect with exponential backoff
- Crash recovery with persistent state

### Plugin System
- **aegis-plugin-sdk**: Rust SDK for building plugins
- **aegis-plugin-runtime**: Sandboxed execution environment
- **aegis-cli**: Command-line tool for developers
- **Marketplace**: Plugin discovery and installation

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.13+
- Rust (for building the agent)

### Development Setup

1. **Clone and start infrastructure:**
```bash
git clone https://github.com/aegis-cloud/aegis-cloud.git
cd aegis-cloud
docker compose up -d postgres redis
```

2. **Start the backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

3. **Start the frontend:**
```bash
cd frontend
npm install
npm run dev
```

4. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

### Production Deployment

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Project Structure

```
aegis-cloud/
├── frontend/                    # Next.js application
│   ├── src/
│   │   ├── app/                 # App router pages
│   │   │   ├── page.tsx         # Landing page
│   │   │   ├── auth/            # Auth pages (login, register, forgot-password)
│   │   │   └── dashboard/       # Dashboard pages
│   │   │       ├── devices/     # Device management
│   │   │       ├── ai/          # AI chat interface
│   │   │       ├── tasks/       # Task management
│   │   │       ├── files/       # File manager
│   │   │       ├── history/     # Execution history
│   │   │       ├── billing/     # Subscription management
│   │   │       ├── settings/    # User settings
│   │   │       └── account/     # Account management
│   │   ├── components/          # Reusable components
│   │   │   ├── ui/              # Base UI components
│   │   │   ├── layout/          # Layout components
│   │   │   └── landing/         # Landing page sections
│   │   ├── lib/                 # Utilities and API client
│   │   ├── stores/              # Zustand stores
│   │   ├── hooks/               # Custom hooks
│   │   └── types/               # TypeScript types
│   └── package.json
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── main.py              # Application entry point
│   │   ├── core/                # Core utilities
│   │   │   ├── config.py        # Settings management
│   │   │   ├── security.py      # Auth, JWT, 2FA
│   │   │   ├── rate_limit.py    # Rate limiting with Redis
│   │   │   └── logging.py       # Structured logging
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic (AI service)
│   │   ├── api/v1/
│   │   │   ├── endpoints/       # API route handlers
│   │   │   └── deps/            # Dependencies (auth)
│   │   └── db/                  # Database session
│   └── requirements.txt
├── agent/                       # Rust Windows Agent
│   ├── src/
│   │   ├── main.rs              # Entry point
│   │   ├── ws/client.rs         # WebSocket client
│   │   ├── tools/executor.rs    # Tool execution
│   │   ├── system/info.rs       # System information
│   │   └── service/             # Windows service integration
│   └── Cargo.toml
└── docs/                        # Documentation
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login with email/password |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Logout |
| GET | `/api/v1/auth/me` | Get current user |
| POST | `/api/v1/auth/forgot-password` | Request password reset |
| POST | `/api/v1/auth/reset-password` | Reset password with token |
| POST | `/api/v1/auth/verify-email` | Verify email address |
| POST | `/api/v1/auth/2fa/enable` | Enable 2FA |
| POST | `/api/v1/auth/2fa/verify` | Verify 2FA code |

### Devices
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/devices` | List all devices |
| GET | `/api/v1/devices/:id` | Get device details |
| POST | `/api/v1/devices/pair` | Pair device with code |
| POST | `/api/v1/devices/pair-code` | Generate pair code |
| PATCH | `/api/v1/devices/:id` | Rename device |
| DELETE | `/api/v1/devices/:id` | Remove device |
| POST | `/api/v1/devices/:id/restart` | Restart device |
| POST | `/api/v1/devices/:id/shutdown` | Shutdown device |
| POST | `/api/v1/devices/:id/wake` | Wake-on-LAN |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tasks` | List tasks |
| GET | `/api/v1/tasks/:id` | Get task details |
| POST | `/api/v1/tasks` | Create task |
| POST | `/api/v1/tasks/:id/cancel` | Cancel task |
| POST | `/api/v1/tasks/:id/retry` | Retry task |

### AI Assistant
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ai/chat` | Send message to AI |

### Billing
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/billing/subscription` | Get subscription |
| POST | `/api/v1/billing/checkout` | Create checkout session |
| POST | `/api/v1/billing/cancel` | Cancel subscription |

### WebSocket Events
| Direction | Event | Description |
|-----------|-------|-------------|
| Server → Client | `connected` | Connection established |
| Server → Client | `device_connected` | Device came online |
| Server → Client | `device_disconnected` | Device went offline |
| Server → Client | `task_progress` | Task progress update |
| Server → Client | `task_completed` | Task finished |
| Server → Client | `live_stats` | Real-time device stats |
| Server → Client | `notification` | New notification |
| Server → Client | `heartbeat_ack` | Heartbeat acknowledgment |
| Client → Server | `subscribe_device` | Subscribe to device events |
| Client → Server | `heartbeat` | Keep-alive ping |

## AI Tools (Approved)

The AI assistant only invokes pre-approved tools exposed by the Windows Agent:

### System
- `system_info` — Get detailed system information
- `cpu_usage` — Current CPU usage
- `ram_usage` — Current RAM usage
- `gpu_usage` — GPU usage and VRAM
- `disk_usage` — Disk usage per drive

### Optimization
- `clean_temp` — Clean temporary files
- `empty_recycle_bin` — Empty Recycle Bin
- `flush_dns` — Flush DNS cache
- `restart_explorer` — Restart Windows Explorer
- `storage_analysis` — Analyze disk usage

### Processes
- `list_processes` — List running processes
- `kill_process` — Terminate a process

### Services
- `list_services` — List Windows services
- `start_service` / `stop_service` / `restart_service`

### Startup
- `list_startup` — List startup applications
- `enable_startup` / `disable_startup`

### Files
- `search_files` / `download_file` / `upload_file`
- `delete_file` / `rename_file` / `move_file`

### Network
- `network_info` / `wifi_info` / `public_ip` / `local_ip`

### Software
- `installed_apps` — List installed applications
- `uninstall_app` — Remove an application

### Security
- `defender_status` — Windows Defender status
- `firewall_status` — Firewall status
- `windows_update_status` — Update status

### Maintenance
- `run_sfc` — System File Checker
- `run_dism` — DISM repair

## Plugin Ecosystem

Build custom tools for Aegis Cloud with our Rust SDK.

### Quick Start

```bash
# Install the CLI
cargo install aegis-cli

# Create a new plugin
aegis plugin init my-plugin
cd my-plugin

# Write your tool
cat > src/lib.rs << 'EOF'
use aegis_plugin_runtime::prelude::*;
use aegis_plugin_sdk::tool;

#[tool(
    name = "get_uptime",
    description = "Get system uptime",
    category = "system",
    risk_level = "low"
)]
async fn get_uptime() -> ToolResult {
    let uptime = get_system_uptime()?;
    Ok(ToolOutput::success(serde_json::json!({
        "seconds": uptime,
        "human": format_duration(uptime)
    })))
}
EOF

# Build and publish
aegis plugin build --release
aegis plugin validate
aegis plugin publish
```

### Available Tools

Your plugins can access:
- **System Information**: Hardware specs, OS info, drivers
- **Process Management**: List, kill, prioritize processes
- **File Operations**: Search, read, write, compress files
- **Network Utilities**: Ping, traceroute, port scanning
- **Service Control**: Start, stop, configure Windows services
- **Registry Access**: Read/write registry keys
- **Performance Monitoring**: Real-time CPU, RAM, disk metrics
- **Security Tools**: Firewall rules, Defender status, audit logs

### Plugin Examples

**System Diagnostics** (`system-diagnostics`)
- `get_cpu_temp` — CPU temperature
- `get_disk_health` — SMART status
- `check_drivers` — Driver versions

**Docker Management** (`docker-manager`)
- `docker_ps` — List containers
- `docker_stop` — Stop container
- `docker_logs` — View logs

**Network Tools** (`network-tools`)
- `speed_test` — Internet speed test
- `port_scan` — Scan open ports
- `dns_lookup` — DNS queries

**Gaming Optimization** (`gaming-pack`)
- `game_mode` — Enable game mode
- `optimize_gpu` — GPU optimization
- `disable_services` — Disable background services

### Security Model

All plugins run in a **sandboxed environment**:
- **Filesystem**: Limited to plugin directory and temp files
- **Network**: No outbound connections unless explicitly granted
- **Memory**: Limited to 100MB per plugin
- **Execution**: Maximum 30 seconds per tool
- **Signature**: All plugins must be code-signed

**High-risk operations** require admin approval:
- Process termination
- Service control
- Registry modifications
- System configuration changes

### Publishing Flow

```
Developer writes tool
    ↓
cargo build --release
    ↓
aegis plugin validate (security check)
    ↓
aegis plugin publish (upload to marketplace)
    ↓
Aegis Cloud signs plugin (Ed25519)
    ↓
Available in marketplace
    ↓
Users install with one click
    ↓
Agent downloads and verifies signature
    ↓
Plugin executes in sandbox
```

---

## For Developers

### Build a Plugin

```bash
cargo install aegis-cli
aegis plugin init my-plugin
cd my-plugin
aegis plugin build --release
aegis plugin publish
```

See the [Plugin Developer Guide](docs/PLUGIN_DEVELOPER_GUIDE.md) for complete documentation.

### Example Plugin

```rust
use aegis_plugin_runtime::prelude::*;
use aegis_plugin_sdk::tool;

#[tool(
    name = "find_large_files",
    description = "Find files larger than 100MB",
    category = "file",
    risk_level = "low"
)]
async fn find_large_files(params: serde_json::Value) -> ToolResult {
    let path = params.get("path").and_then(|v| v.as_str()).unwrap_or("C:\\");
    
    let mut large_files = Vec::new();
    
    for entry in WalkDir::new(path) {
        let entry = entry?;
        if entry.file_type().is_file() {
            let metadata = entry.metadata()?;
            if metadata.len() > 100 * 1024 * 1024 {
                large_files.push(serde_json::json!({
                    "path": entry.path().to_string_lossy(),
                    "size_mb": metadata.len() / 1024 / 1024
                }));
            }
        }
    }
    
    Ok(ToolOutput::success(serde_json::json!({
        "files": large_files,
        "count": large_files.len()
    })))
}
```

---

## For Enterprises

### Deployment Options

**Self-Hosted**
- Deploy on your own infrastructure
- Full control over data and configuration
- Custom integrations with existing systems

**Cloud-Hosted**
- Managed by Aegis Cloud
- Automatic updates and maintenance
- 99.9% uptime SLA

**Hybrid**
- Control plane in cloud
- Data processing on-premises
- Best of both worlds

### Integration

**API Access**
- RESTful API for automation
- Webhook support for events
- GraphQL for complex queries

**SSO Integration**
- SAML 2.0
- OAuth 2.0
- OpenID Connect
- Active Directory

**Compliance**
- SOC 2 Type II
- ISO 27001
- GDPR
- HIPAA (with BAA)

### Support

- **Community**: Free, Discord and forums
- **Business**: $29/mo per device, email support
- **Enterprise**: Custom pricing, dedicated support, SLA guarantees

---

## Billing Plans

| Plan | Price | Devices | AI Queries | Support |
|------|-------|---------|------------|---------|
| Free | $0/mo | 2 | 5/day | Community |
| Pro | $9/mo | 10 | Unlimited | Email |
| Business | $29/mo | 50 | Unlimited | Priority |
| Enterprise | Custom | Unlimited | Unlimited | Dedicated |

All plans include:
- Full plugin marketplace access
- All built-in skills
- Real-time monitoring
- Audit logs
- API access

## Security

### Core Security

- **End-to-end encryption**: TLS 1.3 for all WebSocket connections
- **JWT Authentication**: Short-lived access tokens (30min) with refresh tokens (7 days)
- **Two-Factor Authentication**: TOTP-based 2FA with QR code setup
- **Secure Device Pairing**: One-time codes with expiration
- **Zero Trust AI**: AI only invokes approved tools, never arbitrary commands
- **Role-Based Access Control**: User and Admin roles
- **Rate Limiting**: Per-IP rate limiting via Redis
- **Audit Logging**: Complete audit trail of all actions
- **API Keys**: For programmatic access with expiration

### Device Security

- **mTLS**: Mutual TLS with X.509 certificates
- **Device Fingerprinting**: Hardware-based unique identifiers
- **Certificate Revocation**: CRL and OCSP support
- **Secure Boot**: Agent binary signature verification
- **TPM Integration**: Hardware-backed key storage (optional)

### Plugin Security

- **Sandboxed Execution**: Plugins run in isolated environment
- **Code Signing**: Ed25519 signatures verified before execution
- **Permission Model**: Granular permissions per tool
- **Approval Workflow**: Admin approval for high-risk operations
- **Resource Limits**: Memory and execution time limits
- **Dangerous Pattern Detection**: Blocks common attack patterns
- **Security Scanning**: Automated vulnerability scanning

### Network Security

- **Firewall Friendly**: Outbound connections only (no inbound ports required)
- **Proxy Support**: HTTP/HTTPS/SOCKS5 proxy configuration
- **VPN Compatible**: Works through corporate VPNs
- **Network Isolation**: Separate control and data planes

## Billing Plans

| Plan | Price | Devices | AI Queries |
|------|-------|---------|------------|
| Free | $0/mo | 2 | 5/day |
| Pro | $9/mo | 10 | Unlimited |
| Business | $29/mo | 50 | Unlimited |
| Enterprise | Custom | Unlimited | Unlimited |

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/aegis_cloud
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
GITHUB_CLIENT_ID=xxx
GITHUB_CLIENT_SECRET=xxx
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@aegiscloud.io
SMTP_PASSWORD=xxx
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
```

### Agent
```
AEGIS_SERVER_URL=ws://your-server.com:8000
AEGIS_DEVICE_TOKEN=your-device-token
```

## License

MIT © Aegis Cloud
