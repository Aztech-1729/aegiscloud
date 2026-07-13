# Aegis Cloud Threat Model

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Endpoints                               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐         │
│  │ Website  │─────▶│ Backend  │─────▶│ Redis    │         │
│  │ (Next.js)│      │ (FastAPI)│      │          │         │
│  └──────────┘      └────┬─────┘      └──────────┘         │
│                         │                                   │
│                    ┌────▼─────┐                            │
│                    │PostgreSQL│                            │
│                    └──────────┘                            │
│                         │                                   │
│                    ┌────▼─────┐                            │
│                    │WebSocket │                            │
│                    └────┬─────┘                            │
│                         │                                   │
│                    ┌────▼─────┐                            │
│                    │  Agent   │                            │
│                    │  (Rust)  │                            │
│                    └────┬─────┘                            │
│                         │                                   │
│                    ┌────▼─────┐                            │
│                    │ Windows  │                            │
│                    │   APIs   │                            │
│                    └──────────┘                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Threat Analysis

### 1. Website → Backend

**Attack Vector**: Compromise website or intercept traffic

**Threats**:
- **Man-in-the-Middle (MITM)**: Intercept HTTPS traffic
  - Mitigation: Enforce HTTPS, HSTS, certificate pinning
  - Risk: Medium (if HTTP used), Low (if HTTPS enforced)

- **Cross-Site Scripting (XSS)**: Inject malicious scripts
  - Mitigation: Content Security Policy, input sanitization, React auto-escaping
  - Risk: Low (React handles most XSS)

- **Cross-Site Request Forgery (CSRF)**: Force authenticated actions
  - Mitigation: SameSite cookies, CSRF tokens, Origin validation
  - Risk: Low (JWT in Authorization header)

- **Session Hijacking**: Steal JWT tokens
  - Mitigation: Short-lived tokens (30min), secure storage (httpOnly cookies), token rotation
  - Risk: Medium

**If attacker controls this**: Can make authenticated API requests as any user

---

### 2. Backend → Redis

**Attack Vector**: Compromise backend or Redis credentials

**Threats**:
- **Unauthorized Access**: Read/write Redis data
  - Mitigation: Redis AUTH, network isolation, firewall rules
  - Risk: High (cache contains sessions, rate limits)

- **Cache Poisoning**: Inject malicious data into cache
  - Mitigation: Input validation, signed cache entries, TTL
  - Risk: Medium

- **Denial of Service**: Flood Redis with requests
  - Mitigation: Rate limiting, connection pooling, memory limits
  - Risk: Medium

**If attacker controls this**: Can steal sessions, bypass rate limits, manipulate queues

---

### 3. Backend → PostgreSQL

**Attack Vector**: SQL injection, credential theft

**Threats**:
- **SQL Injection**: Inject malicious SQL
  - Mitigation: Parameterized queries (SQLAlchemy ORM), input validation
  - Risk: Low (ORM prevents most SQLi)

- **Data Exfiltration**: Read entire database
  - Mitigation: Least privilege DB user, network isolation, encryption at rest
  - Risk: High

- **Data Tampering**: Modify database records
  - Mitigation: Audit logs, row-level security, application-level validation
  - Risk: High

**If attacker controls this**: Full access to all user data, devices, commands

---

### 4. Backend ↔ Agent (WebSocket)

**Attack Vector**: MITM, token theft, replay attacks

**Threats**:
- **Man-in-the-Middle**: Intercept WebSocket traffic
  - Mitigation: WSS (TLS), certificate pinning, mutual TLS
  - Risk: High (commands sent over WebSocket)

- **Token Theft**: Steal device token
  - Mitigation: Token rotation, short expiration, secure storage
  - Risk: High (attacker can impersonate device)

- **Replay Attack**: Replay captured WebSocket messages
  - Mitigation: Nonce for every command, timestamp validation
  - Risk: High (could replay destructive commands)

- **Command Injection**: Inject malicious commands
  - Mitigation: Tool registry (only approved tools), parameter validation
  - Risk: Medium (tool registry prevents arbitrary execution)

**If attacker controls this**: Can execute commands on devices, steal data, install malware

---

### 5. Agent → Windows APIs

**Attack Vector**: Compromise agent binary, privilege escalation

**Threats**:
- **Binary Tampering**: Replace agent executable
  - Mitigation: Code signing, signature verification, auto-update checks
  - Risk: Critical (full system compromise)

- **Privilege Escalation**: Gain SYSTEM privileges
  - Mitigation: Run as SYSTEM intentionally, restrict API calls, sandboxing
  - Risk: High (by design, but limits exposure)

- **DLL Hijacking**: Load malicious DLLs
  - Mitigation: Secure DLL search path, code signing, minimal dependencies
  - Risk: Medium

- **Memory Dump**: Extract secrets from memory
  - Mitigation: Minimize sensitive data in memory, encrypt tokens at rest
  - Risk: Medium

**If attacker controls this**: Full control of Windows system, data theft, lateral movement

---

## Attack Surface Summary

| Component | Risk Level | Primary Threats |
|-----------|------------|-----------------|
| Website | Medium | XSS, CSRF, session hijacking |
| Backend API | High | Auth bypass, SQLi, data exfiltration |
| Redis | High | Session theft, cache poisoning |
| PostgreSQL | Critical | Data breach, tampering |
| WebSocket | Critical | MITM, token theft, replay attacks |
| Agent | Critical | Binary tampering, privilege escalation |

---

## Security Controls

### Authentication & Authorization
- ✅ JWT with short expiration (30min)
- ✅ Refresh token rotation
- ✅ Two-factor authentication (TOTP)
- ✅ Device token separation from user auth
- ✅ Role-based access control (5 roles)

### Encryption
- ✅ TLS 1.3 for all connections (HTTPS, WSS)
- ✅ Password hashing (bcrypt, 12 rounds)
- ✅ Sensitive data encrypted at rest
- ✅ Device token encryption in storage

### Input Validation
- ✅ Pydantic schemas for all API inputs
- ✅ JSON Schema validation for tool parameters
- ✅ Tool registry (no arbitrary command execution)
- ✅ SQL injection prevention (ORM)

### Network Security
- ✅ Firewall rules (only 443 exposed)
- ✅ Network isolation (Redis, PostgreSQL not public)
- ✅ Rate limiting per IP and user
- ✅ DDoS protection (Cloudflare/AWS Shield)

### Audit & Monitoring
- ✅ Audit logs for all actions
- ✅ Command execution logging
- ✅ WebSocket connection tracking
- ✅ Failed login monitoring
- ✅ Anomaly detection (unusual patterns)

### Incident Response
- ✅ Automated alerting (Prometheus + Grafana)
- ✅ Log aggregation (ELK stack)
- ✅ Incident response playbook
- ✅ Disaster recovery plan
- ✅ Regular security audits

---

## Compliance

- **GDPR**: Data encryption, right to deletion, consent management
- **SOC 2**: Audit logs, access controls, encryption
- **ISO 27001**: Security management system
- **HIPAA**: (if healthcare customers) PHI encryption, access logs

---

## Penetration Testing Recommendations

### Priority 1: Critical
1. WebSocket security (MITM, replay attacks)
2. Agent binary signing and verification
3. JWT token forgery and replay
4. SQL injection in all endpoints

### Priority 2: High
1. Privilege escalation paths
2. Rate limit bypass techniques
3. Session hijacking methods
4. Cross-site scripting vectors

### Priority 3: Medium
1. Information disclosure
2. Denial of service vectors
3. Configuration weaknesses
4. Dependency vulnerabilities

---

## Threat Model Version History

- **v1.0** (2024-01-15): Initial threat model
- **v1.1** (2024-01-20): Added WebSocket threat analysis
- **v1.2** (2024-02-01): Added agent security considerations
