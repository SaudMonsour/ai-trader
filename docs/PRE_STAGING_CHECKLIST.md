# Phase 1 MVP - Final Pre-Staging Checklist

**Status**: ✅ Ready for Staging Deployment

---

## Critical Security Reminders

- [ ] **DO NOT** store emergency token in repo or logs (only SHA256 hash in env)
- [ ] Confirm `CLEAR_EMERGENCY_HASH` is in staging secret store
- [ ] Verify all API keys are in environment variables (not in code)
- [ ] `.env` file is in `.gitignore`
- [ ] Token rotation process documented and access restricted

---

## Infrastructure Setup

### 1. Environment Variables (Staging)

```bash
# Emergency stop clearance (SHA256 of token)
export CLEAR_EMERGENCY_HASH=$(echo -n "clear-emergency-2026-02" | sha256sum | awk '{print $1}')

# Broker API credentials
export BROKER_API_KEY="your_broker_key_here"
export NEWS_API_KEY="your_news_api_key_here"

# Telegram alerting (optional but recommended)
export TG_BOT_TOKEN="123456:ABC-DEF..."
export TG_CHAT_ID="-1001234567890"

# System configuration
export SYSTEM_MODE="paper"
export SYSTEM_DRY_RUN="true"
```

### 2. Logging Configuration

- [ ] Enable **stdout logging** for container log capture
- [ ] Configure log rotation (see `logrotate.conf` when generated)
- [ ] Set up log forwarding to central logging system (optional)

### 3. Alerting

- [ ] Configure Telegram bot token and chat ID
- [ ] Test alert: `python tools/alert_telegram.py "Test alert from staging"`
- [ ] Set up alerts for:
  - Failed state writes
  - Reconciliation errors
  - Repeated order failures
  - Emergency stop cleared

### 4. Branch Protection

- [ ] Protect `staging` branch (require PR + CI passing + 1 approval)
- [ ] Protect `main` branch (require PR + CI passing + 1 approval)
- [ ] See `docs/BRANCH_PROTECTION.md` for setup instructions

---

## Deployment Steps

### 1. Pre-Flight Checks

```bash
# Run all tests locally
pytest test_feedback_verification.py -q

# Verify no secrets in code
git grep -i "api_key" src/
git grep -i "token" src/ | grep -v "# token"

# Check .gitignore
cat .gitignore | grep -E "\.env|secrets|\.key"
```

### 2. Docker Compose Deployment

```bash
# Build and start services
docker-compose up -d

# Check health
curl http://localhost:8000/health | jq .

# View logs
docker-compose logs -f trading-agent
docker-compose logs -f health-api
```

### 3. First 24 Hours Monitoring

- [ ] Check `/health` endpoint every 5 minutes
- [ ] Monitor `logs/trading.log` for errors
- [ ] Verify order reconciliation on container restart
- [ ] Confirm no duplicate orders
- [ ] Check portfolio balance updates
- [ ] Test emergency stop set/clear with token

### 4. Smoke Tests

```bash
# Test emergency stop
python -c "from src.utils.state_manager import get_state_manager; get_state_manager().set_emergency_stop(True)"

# Verify blocked execution (check logs)
docker-compose logs trading-agent | grep "EMERGENCY STOP"

# Clear emergency stop
python tools/clear_emergency.py --confirm clear-emergency-2026-02

# Verify clearance in audit trail
cat data/state.json | jq '.audit[-1]'
```

---

## Rollback Plan

If issues occur in staging:

```bash
# 1. Enable emergency stop
python -c "from src.utils.state_manager import get_state_manager; get_state_manager().set_emergency_stop(True)"

# 2. Stop containers
docker-compose down

# 3. Restore state backup
cp data/backups/state_$(date +%Y%m%d)_*.json data/state.json

# 4. Checkout previous stable version
git checkout <previous-tag>

# 5. Rebuild and restart
docker-compose up -d --build

# 6. Alert team
python tools/alert_telegram.py "⚠️ ROLLBACK: Trading agent reverted to previous version"
```

---

## Success Criteria (24-72 hours)

After 24-72 hours of stable operation:

- [ ] No critical errors in logs
- [ ] All reconciliations successful
- [ ] No duplicate orders detected
- [ ] Portfolio balances accurate
- [ ] Health endpoint consistently returns 200 OK
- [ ] Emergency stop set/clear working correctly
- [ ] CI pipeline passing on all PRs
- [ ] Alerts firing correctly for test scenarios

---

## Next Steps After Staging Success

1. **Production Planning**
   - Review staging metrics and logs
   - Identify any performance bottlenecks
   - Update risk parameters based on staging data

2. **Phase 2 Features**
   - Backtester implementation
   - Advanced risk models
   - Dashboard/monitoring UI
   - Multi-asset support
   - Enhanced signal generation

3. **Production Deployment**
   - Migrate to live broker connections (when ready)
   - Set `SYSTEM_MODE=live` and `SYSTEM_DRY_RUN=false`
   - Start with minimal capital
   - Gradual ramp-up

---

## Artifacts Created

### Code & Configuration
- ✅ `.github/workflows/ci.yml` - CI/CD pipeline
- ✅ `src/infra/health.py` - Health & metrics API
- ✅ `tools/clear_emergency.py` - Token-based emergency clearance
- ✅ `docker-compose.override.yml` - Staging deployment config
- ✅ `tools/alert_telegram.py` - Telegram alerting

### Documentation
- ✅ `COMPLETE_DOCUMENTATION.md` - Comprehensive guide
- ✅ `docs/BRANCH_PROTECTION.md` - Branch protection setup
- ✅ `docs/PRE_STAGING_CHECKLIST.md` - This file

### Pending (to be generated)
- ⏳ `logrotate.conf` - Log rotation configuration
- ⏳ GitHub Actions secrets setup guide

---

**Status**: Ready for staging deployment after logrotate and secrets guides are added.
