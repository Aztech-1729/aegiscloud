# Aegis Cloud API Documentation

## Base URL

```
Production: https://api.aegiscloud.io
Staging: https://api-staging.aegiscloud.io
Development: http://localhost:8000
```

## Authentication

### JWT Bearer Token

All authenticated endpoints require a JWT token in the Authorization header:

```http
Authorization: Bearer <access_token>
```

### Getting a Token

**Register**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Login**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Token Refresh

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGc..."
}
```

Response:
```json
{
  "access_token": "new_access_token...",
  "refresh_token": "new_refresh_token...",
  "token_type": "bearer"
}
```

### Token Expiration

- Access tokens: 30 minutes
- Refresh tokens: 7 days

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login | No |
| POST | `/auth/refresh` | Refresh token | No |
| POST | `/auth/logout` | Logout | Yes |
| GET | `/auth/me` | Get current user | Yes |
| PUT | `/auth/me` | Update user profile | Yes |
| POST | `/auth/forgot-password` | Request password reset | No |
| POST | `/auth/reset-password` | Reset password | No |
| POST | `/auth/verify-email` | Verify email | No |
| POST | `/auth/2fa/enable` | Enable 2FA | Yes |
| POST | `/auth/2fa/verify` | Verify 2FA code | Yes |
| POST | `/auth/2fa/disable` | Disable 2FA | Yes |

### Devices

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/devices` | List all devices | Yes |
| GET | `/devices/{id}` | Get device details | Yes |
| POST | `/devices` | Create device | Yes |
| PATCH | `/devices/{id}` | Update device | Yes |
| DELETE | `/devices/{id}` | Delete device | Yes |
| POST | `/devices/{id}/restart` | Restart device | Yes |
| POST | `/devices/{id}/shutdown` | Shutdown device | Yes |
| POST | `/devices/{id}/wake` | Wake device (WOL) | Yes |
| POST | `/devices/pair` | Pair device | Yes |
| POST | `/devices/pair-code` | Generate pair code | Yes |

### Commands

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/commands` | List commands | Yes |
| GET | `/commands/{id}` | Get command details | Yes |
| POST | `/commands` | Create command | Yes |
| POST | `/commands/{id}/cancel` | Cancel command | Yes |
| POST | `/commands/{id}/retry` | Retry command | Yes |
| POST | `/commands/{id}/approve` | Approve command | Yes |

### Tools

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/tools` | List all tools | Yes |
| GET | `/tools/{name}` | Get tool details | Yes |
| GET | `/tools/categories` | List tool categories | Yes |
| POST | `/tools/{name}/validate` | Validate tool parameters | Yes |

### Skills

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/skills` | List all skills | Yes |
| GET | `/skills/{id}` | Get skill details | Yes |
| GET | `/skills/categories` | List skill categories | Yes |
| POST | `/skills/{id}/execute` | Execute skill | Yes |

### Policies

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/policies` | List policies | Yes |
| GET | `/policies/templates` | List policy templates | Yes |
| POST | `/policies/create-from-template/{id}` | Create policy from template | Yes |
| PATCH | `/policies/{id}/toggle` | Enable/disable policy | Yes |
| DELETE | `/policies/{id}` | Delete policy | Yes |

### Schedules

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/schedules` | List schedules | Yes |
| POST | `/schedules` | Create schedule | Yes |
| PATCH | `/schedules/{id}/toggle` | Enable/disable schedule | Yes |
| DELETE | `/schedules/{id}` | Delete schedule | Yes |

### Plugins

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/plugins` | List available plugins | Yes |
| GET | `/plugins/installed` | List installed plugins | Yes |
| POST | `/plugins/{id}/install` | Install plugin | Yes |
| DELETE | `/plugins/{id}/uninstall` | Uninstall plugin | Yes |

### Organizations

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/organizations` | Get user's organization | Yes |
| GET | `/organizations/departments` | List departments | Yes |
| GET | `/organizations/members` | List members | Yes |
| POST | `/organizations/invite` | Invite member | Yes |

### Memory

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/memory/{device_id}` | Get device memory | Yes |
| GET | `/memory/{device_id}/recommendations` | Get recommendations | Yes |
| GET | `/memory/{device_id}/ai-context` | Get AI context | Yes |
| POST | `/memory/{device_id}/preferences` | Update preferences | Yes |

### Events

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/events` | Get recent events | Yes |
| GET | `/events/stream` | Get WebSocket endpoint | Yes |

### Certificates

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/certificates/enroll/{device_id}` | Enroll device certificate | Yes |
| POST | `/certificates/renew/{device_id}` | Renew certificate | Yes |
| GET | `/certificates/{device_id}` | Get device certificate | Yes |
| GET | `/certificates/ca/certificate` | Get CA certificate | Yes |
| GET | `/certificates/ca/crl` | Get CRL | Yes |

### Notifications

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/notifications` | List notifications | Yes |
| PATCH | `/notifications/{id}/read` | Mark as read | Yes |
| PATCH | `/notifications/read-all` | Mark all as read | Yes |

### Billing

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/billing/subscription` | Get subscription | Yes |
| POST | `/billing/checkout` | Create checkout session | Yes |
| POST | `/billing/cancel` | Cancel subscription | Yes |

### Settings

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/settings` | Get user settings | Yes |
| PATCH | `/settings` | Update settings | Yes |

### Admin

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/admin/users` | List users | Admin |
| GET | `/admin/stats` | Get platform stats | Admin |
| PUT | `/admin/users/{id}/toggle-active` | Toggle user active | Admin |
| GET | `/admin/devices` | List all devices | Admin |
| GET | `/admin/commands` | List all commands | Admin |

### History

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/history` | Get command history | Yes |
| GET | `/history/export` | Export history | Yes |

### Audit

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/audit` | Get audit logs | Yes |
| GET | `/audit/admin` | Get all audit logs | Admin |

## Rate Limiting

| Plan | Requests/minute | Commands/hour |
|------|-----------------|---------------|
| Free | 60 | 100 |
| Pro | 300 | 1000 |
| Business | 1000 | 5000 |
| Enterprise | 10000 | Unlimited |

Rate limit headers:
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640995200
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded",
  "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## WebSocket

### Client Connection

```javascript
const ws = new WebSocket('wss://api.aegiscloud.io/ws?token=<access_token>');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};

ws.onclose = (event) => {
  console.log('WebSocket closed:', event.code, event.reason);
};
```

### Agent Connection

```rust
let ws_url = format!("wss://api.aegiscloud.io/ws/agent?device_token={}", device_token);
let (ws_stream, _) = connect_async(&ws_url).await?;
```

### Event Types

- `device.connected` - Device came online
- `device.disconnected` - Device went offline
- `command.started` - Command execution started
- `command.completed` - Command completed successfully
- `command.failed` - Command failed
- `notification` - New notification

## SDK Examples

### Python

```python
import requests

# Login
response = requests.post(
    "https://api.aegiscloud.io/api/v1/auth/login",
    json={"email": "user@example.com", "password": "password123"}
)
token = response.json()["access_token"]

# List devices
headers = {"Authorization": f"Bearer {token}"}
devices = requests.get(
    "https://api.aegiscloud.io/api/v1/devices",
    headers=headers
).json()

# Execute skill
requests.post(
    "https://api.aegiscloud.io/api/v1/skills/gaming-optimization/execute",
    json={"device_id": "device-123"},
    headers=headers
)
```

### JavaScript

```javascript
// Login
const response = await fetch('https://api.aegiscloud.io/api/v1/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({email: 'user@example.com', password: 'password123'})
});
const {access_token} = await response.json();

// List devices
const devices = await fetch('https://api.aegiscloud.io/api/v1/devices', {
  headers: {'Authorization': `Bearer ${access_token}`}
}).then(r => r.json());

// Execute skill
await fetch('https://api.aegiscloud.io/api/v1/skills/gaming-optimization/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({device_id: 'device-123'})
});
```

## Versioning

API versioning is done via URL path:
- `/api/v1/` - Current stable version
- `/api/v2/` - Next major version (in development)

## Support

- Documentation: https://docs.aegiscloud.io
- API Status: https://status.aegiscloud.io
- Support Email: api-support@aegiscloud.io
- Discord: https://discord.gg/aegiscloud
