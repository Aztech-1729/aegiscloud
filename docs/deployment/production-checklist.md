# Production Deployment Checklist

## Pre-Deployment

### Code Quality
- [ ] All tests passing (backend, frontend, agent)
- [ ] Code coverage >80% on critical paths
- [ ] No TODO/FIXME comments in production code
- [ ] No console.log in frontend
- [ ] No unsafe blocks in Rust agent
- [ ] All dependencies up to date (no known vulnerabilities)
- [ ] Cargo audit clean (Rust dependencies)
- [ ] Bandit security scan clean (Python)

### Security
- [ ] Penetration test completed
- [ ] OWASP Top 10 vulnerabilities addressed
- [ ] HTTPS enforced with HSTS
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (React auto-escaping)
- [ ] CSRF protection enabled
- [ ] Secret keys rotated
- [ ] Database credentials encrypted
- [ ] Code signing configured for Windows agent

### Infrastructure
- [ ] Production environment provisioned
- [ ] Load balancer configured
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] DDoS protection enabled
- [ ] Monitoring dashboards created
- [ ] Alert rules configured
- [ ] Log aggregation set up
- [ ] Backup strategy implemented
- [ ] Disaster recovery plan documented

### Database
- [ ] Migrations tested on staging
- [ ] Indexes created for performance
- [ ] Connection pooling configured
- [ ] Read replicas provisioned
- [ ] Automated backups enabled
- [ ] Point-in-time recovery tested
- [ ] Data retention policy defined

### Configuration
- [ ] Environment variables set
- [ ] Secrets stored in vault (AWS Secrets Manager/HashiCorp Vault)
- [ ] CORS origins whitelisted
- [ ] SMTP configured for emails
- [ ] Stripe API keys configured
- [ ] OAuth credentials configured
- [ ] Sentry DSN configured
- [ ] Feature flags configured

### Testing
- [ ] Load test completed (10K agents)
- [ ] Chaos test completed (300s duration)
- [ ] Smoke tests passing
- [ ] End-to-end tests passing
- [ ] WebSocket reconnection tested
- [ ] Agent crash recovery tested
- [ ] Database failover tested
- [ ] Redis failover tested

### Documentation
- [ ] API documentation up to date
- [ ] User guides written
- [ ] Deployment runbook created
- [ ] Incident response plan documented
- [ ] Security policy documented
- [ ] Privacy policy updated
- [ ] Terms of service updated

### Compliance
- [ ] GDPR compliance verified
- [ ] Data processing agreements in place
- [ ] Cookie consent implemented
- [ ] Right to deletion implemented
- [ ] Audit logging enabled
- [ ] Data retention policy defined

## Deployment Steps

### 1. Pre-Deployment (T-1 day)
```bash
# Notify team
slack "#deployments" "Production deployment scheduled for tomorrow at 10:00 UTC"

# Freeze code
git tag v2.0.0-rc1
git push origin v2.0.0-rc1

# Run final tests
./scripts/run-all-tests.sh

# Create deployment branch
git checkout -b deploy/v2.0.0
```

### 2. Deployment (T-0)
```bash
# Backup database
pg_dump -U aegis aegis_cloud > backup-$(date +%Y%m%d).sql

# Deploy backend
kubectl apply -f k8s/backend-deployment.yaml
kubectl rollout status deployment/aegis-backend

# Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml
kubectl rollout status deployment/aegis-frontend

# Deploy agent (if new version)
aws s3 cp agent/target/release/aegis-agent.exe s3://aegis-releases/v2.0.0/
aws cloudfront create-invalidation --distribution-id XXXXX --paths "/agent/*"

# Run database migrations
kubectl exec -it $(kubectl get pod -l app=aegis-backend -o name | head -1) -- alembic upgrade head

# Verify deployment
curl https://api.aegiscloud.io/health
curl https://app.aegiscloud.io
```

### 3. Post-Deployment (T+10 min)
```bash
# Run smoke tests
./scripts/smoke-test.sh https://api.aegiscloud.io

# Check metrics
open https://grafana.aegiscloud.io/d/aegis-overview

# Monitor error rates
kubectl logs -l app=aegis-backend --tail=100

# Check WebSocket connections
kubectl exec -it $(kubectl get pod -l app=aegis-backend -o name | head -1) -- python -c "from app.core.observability import metrics; print(metrics.get_metrics())"

# Notify team
slack "#deployments" "✅ Deployment v2.0.0 successful"
```

### 4. Monitoring (T+1 hour)
```bash
# Check error rates
kubectl logs -l app=aegis-backend --since=1h | grep -c "ERROR"

# Check latency
kubectl logs -l app=aegis-backend --since=1h | grep "request_duration" | awk '{sum+=$2; count++} END {print sum/count}'

# Check agent connections
kubectl exec -it $(kubectl get pod -l app=aegis-backend -o name | head -1) -- python -c "from app.core.observability import metrics; print('Agents:', metrics.get_metrics()['agents_connected'])"

# Check database performance
psql -U aegis -d aegis_cloud -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"
```

## Rollback Plan

### When to Rollback
- Error rate >5%
- P95 latency >2s
- Database connection errors
- WebSocket disconnection rate >10%
- Agent reconnection rate >20%

### Rollback Steps
```bash
# Identify previous stable version
kubectl rollout history deployment/aegis-backend

# Rollback backend
kubectl rollout undo deployment/aegis-backend --to-revision=5

# Rollback frontend
kubectl rollout undo deployment/aegis-frontend --to-revision=5

# Rollback database migrations (if any)
kubectl exec -it $(kubectl get pod -l app=aegis-backend -o name | head -1) -- alembic downgrade -1

# Verify rollback
curl https://api.aegiscloud.io/health

# Notify team
slack "#deployments" "⚠️  Rolled back to v1.9.0"
```

## Post-Deployment Tasks

### Immediate (T+1 day)
- [ ] Review error logs
- [ ] Check user feedback
- [ ] Monitor performance metrics
- [ ] Verify all features working
- [ ] Check agent update success rate

### Short-term (T+1 week)
- [ ] Analyze user engagement
- [ ] Review support tickets
- [ ] Check billing accuracy
- [ ] Verify backup success
- [ ] Review security logs

### Long-term (T+1 month)
- [ ] Performance optimization
- [ ] Feature adoption analysis
- [ ] Customer satisfaction survey
- [ ] Security audit
- [ ] Compliance review

## Emergency Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| DevOps Lead | John Doe | +1-555-0100 | john@aegiscloud.io |
| Backend Lead | Jane Smith | +1-555-0101 | jane@aegiscloud.io |
| Frontend Lead | Bob Johnson | +1-555-0102 | bob@aegiscloud.io |
| Security Lead | Alice Williams | +1-555-0103 | alice@aegiscloud.io |
| On-Call Engineer | (Rotating) | +1-555-0199 | oncall@aegiscloud.io |

## Communication Plan

### Internal
- **Pre-deployment**: Slack #deployments channel
- **During deployment**: Live updates in Slack
- **Post-deployment**: Summary email to engineering team

### External
- **Status page**: https://status.aegiscloud.io
- **Twitter**: @AegisCloud
- **Customer email**: customers@aegiscloud.io
- **Support**: support@aegiscloud.io

---

## Version History

- **v1.0** (2024-01-15): Initial checklist
- **v1.1** (2024-02-01): Added rollback plan
- **v1.2** (2024-03-01): Added emergency contacts
