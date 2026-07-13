# Incident Response Runbook

## Severity Levels

### P0 - Critical
- Complete system outage
- Data breach
- Security compromise
- Revenue impact

**Response Time**: 15 minutes  
**Communication**: Immediate all-hands Slack, customer email within 1 hour

### P1 - High
- Major feature broken
- Significant performance degradation
- Partial outage

**Response Time**: 30 minutes  
**Communication**: Engineering Slack channel, customer status page update within 2 hours

### P2 - Medium
- Minor feature broken
- Performance issues
- Intermittent failures

**Response Time**: 2 hours  
**Communication**: Engineering Slack channel

### P3 - Low
- Cosmetic issues
- Minor bugs
- Feature requests

**Response Time**: Next business day  
**Communication**: Ticket system

---

## Common Incidents

### 1. Backend API Down

**Symptoms**:
- 5xx errors on all endpoints
- Health check failing
- Dashboard showing errors

**Immediate Actions**:
```bash
# Check backend status
kubectl get pods -l app=aegis-backend

# Check logs
kubectl logs -l app=aegis-backend --tail=100

# Restart backend
kubectl rollout restart deployment/aegis-backend

# Verify health
curl https://api.aegiscloud.io/health
```

**Escalation**:
- If restart doesn't fix: Check database connectivity
- If database issue: Check PostgreSQL status and logs
- If persistent: Engage on-call database engineer

**Communication**:
```
🚨 P0 Incident: Backend API Down
Status: Investigating
Impact: All API requests failing
ETA: 30 minutes
```

---

### 2. Database Connection Issues

**Symptoms**:
- Database timeout errors
- Connection pool exhausted
- Slow queries

**Immediate Actions**:
```bash
# Check database status
kubectl get pods -l app=postgres

# Check connections
kubectl exec -it $(kubectl get pod -l app=postgres -o name | head -1) -- psql -U aegis -c "SELECT count(*) FROM pg_stat_activity;"

# Check slow queries
kubectl exec -it $(kubectl get pod -l app=postgres -o name | head -1) -- psql -U aegis -c "SELECT query, state FROM pg_stat_activity WHERE state = 'active' AND query_start < now() - interval '5 minutes';"

# Kill long-running queries
kubectl exec -it $(kubectl get pod -l app=postgres -o name | head -1) -- psql -U aegis -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'active' AND query_start < now() - interval '10 minutes';"
```

**Escalation**:
- If connection pool exhausted: Increase pool size or check for connection leaks
- If slow queries: Optimize queries or add indexes
- If data corruption: Restore from backup

---

### 3. High Agent Disconnect Rate

**Symptoms**:
- Alert: "Agent reconnect rate >20%"
- Many devices showing offline
- WebSocket connection errors

**Immediate Actions**:
```bash
# Check WebSocket server status
kubectl logs -l app=aegis-backend | grep -i "websocket"

# Check Redis pub/sub
kubectl exec -it $(kubectl get pod -l app=redis -o name | head -1) -- redis-cli INFO pubsub

# Restart WebSocket servers
kubectl rollout restart deployment/aegis-websocket
```

**Escalation**:
- If Redis issue: Check Redis cluster health
- If network issue: Check load balancer and network policies
- If agent bug: Rollback agent version

---

### 4. Security Breach

**Symptoms**:
- Unauthorized access detected
- Unusual API calls
- Data exfiltration alerts

**Immediate Actions**:
1. **Isolate**: Disable affected accounts/devices
2. **Investigate**: Check audit logs
3. **Contain**: Revoke tokens, rotate credentials
4. **Notify**: Legal, security team, affected customers

```bash
# Disable user
kubectl exec -it $(kubectl get pod -l app=aegis-backend -o name | head -1) -- python -c "
from app.db.session import get_db
from app.models.models import User
import asyncio

async def disable_user(email):
    async for db in get_db():
        user = await db.execute(select(User).where(User.email == email))
        user = user.scalar_one_or_none()
        if user:
            user.is_active = False
            await db.commit()

asyncio.run(disable_user('compromised@example.com'))
"

# Revoke all tokens for user
kubectl exec -it $(kubectl get pod -l app=redis -o name | head -1) -- redis-cli KEYS "session:*" | xargs redis-cli DEL
```

**Escalation**:
- Legal team immediately
- Security incident response team
- Customer notification within 72 hours (GDPR)
- Law enforcement if required

---

### 5. Data Loss

**Symptoms**:
- Missing data
- Database errors
- Backup failures

**Immediate Actions**:
```bash
# Stop all writes
kubectl scale deployment/aegis-backend --replicas=0

# Restore from backup
kubectl exec -it $(kubectl get pod -l app=postgres -o name | head -1) -- psql -U aegis aegis_cloud < /backups/latest.sql

# Verify data integrity
kubectl exec -it $(kubectl get pod -l app=postgres -o name | head -1) -- psql -U aegis -c "SELECT count(*) FROM users;"

# Resume operations
kubectl scale deployment/aegis-backend --replicas=3
```

**Escalation**:
- Database engineer immediately
- Check point-in-time recovery options
- Notify affected customers

---

## Communication Templates

### Initial Incident Notification

```
🚨 [SEVERITY] Incident: [Title]
Status: Investigating
Impact: [Description]
Affected: [Systems/Users]
ETA: [Time]
Updates: [Channel/Link]
```

### Update During Incident

```
🔄 Update: [Title]
Status: [Current Status]
Progress: [What we're doing]
ETA: [Updated Time]
```

### Incident Resolved

```
✅ Resolved: [Title]
Duration: [Total Time]
Root Cause: [Brief Description]
Impact: [What was affected]
Prevention: [What we're doing to prevent recurrence]
```

---

## Post-Incident Review

### Within 24 Hours

- [ ] Write incident report
- [ ] Collect logs and metrics
- [ ] Interview involved engineers
- [ ] Document timeline
- [ ] Identify root cause

### Within 1 Week

- [ ] Conduct blameless post-mortem
- [ ] Create action items
- [ ] Assign owners and deadlines
- [ ] Update runbooks
- [ ] Share learnings with team

### Within 1 Month

- [ ] Review action item completion
- [ ] Update monitoring/alerting
- [ ] Conduct chaos testing for similar scenarios
- [ ] Update documentation
- [ ] Share company-wide learnings

---

## On-Call Rotation

### Schedule
- Primary: Monday 9am → Friday 9am
- Secondary: Backup for primary
- Handoff: Friday 9am Slack meeting

### Compensation
- On-call stipend: $500/week
- Pager duty compensation: $100/call (10pm-6am)
- Incident response bonus: Based on severity

### Tools
- PagerDuty: Primary alerting
- Slack: #oncall channel
- StatusPage: Customer communication
- Grafana: Monitoring dashboards

---

## Emergency Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| CTO | John Doe | +1-555-0100 | john@aegiscloud.io |
| VP Engineering | Jane Smith | +1-555-0101 | jane@aegiscloud.io |
| Security Lead | Alice Williams | +1-555-0103 | alice@aegiscloud.io |
| Legal Counsel | Bob Johnson | +1-555-0104 | bob@aegiscloud.io |
| PR/Comms | Charlie Brown | +1-555-0105 | charlie@aegiscloud.io |

---

## Version History

- **v1.0** (2024-01-15): Initial runbook
- **v1.1** (2024-02-01): Added security breach procedures
- **v1.2** (2024-03-01): Added post-incident review process
