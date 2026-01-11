# Migru Production Deployment Guide

## Overview

This guide covers deploying Migru for end users with a focus on:
- **Privacy-first**: All data stays local
- **Minimal dependencies**: Only production packages
- **Security**: API key protection and data isolation
- **User-friendly**: Simple setup and operation

## Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows with WSL2
- **Python**: 3.12 or higher
- **Redis**: 6.0 or higher (local only)
- **Disk**: 500MB for application + space for user data
- **RAM**: 512MB minimum, 1GB recommended
- **Network**: Internet connection for AI API calls

### Required API Keys
- **Mistral AI** (required): https://console.mistral.ai/
- **Cerebras** (recommended for speed): https://cerebras.ai/
- **OpenRouter** (optional backup): https://openrouter.ai/

### Optional API Keys
- **Firecrawl** (optional search): https://firecrawl.dev/
- **OpenWeather** (optional context): https://openweathermap.org/api

## Installation for End Users

### Quick Setup (Recommended)

```bash
# 1. Clone or download Migru
git clone https://github.com/Ash-Blanc/migru.git
cd migru

# 2. Run automated setup
./setup.sh
```

The setup script will:
- Install uv (Python package manager)
- Install only production dependencies
- Create `.env` file from template
- Verify Redis installation
- Run production checks

### Manual Setup

```bash
# 1. Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install production dependencies only
uv pip install -e .

# 4. Install Redis (if not installed)
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS:
brew install redis

# 5. Copy environment template
cp .env.example .env

# 6. Edit .env and add your API keys
nano .env  # or your preferred editor
```

### Configuration

Edit `.env` with your API keys:

```env
# Required
MISTRAL_API_KEY=your_mistral_key_here

# Recommended (for speed)
CEREBRAS_API_KEY=your_cerebras_key_here

# Optional
OPENROUTER_API_KEY=your_openrouter_key_here
FIRECRAWL_API_KEY=your_firecrawl_key_here
OPENWEATHER_API_KEY=your_openweather_key_here

# Local Redis (default)
REDIS_URL=redis://localhost:6379
```

## Security Checklist

### Before Running in Production

```bash
# 1. Run production validation
python -m app.production

# 2. Check file permissions
chmod 600 .env
chmod 700 app/

# 3. Verify .gitignore
cat .gitignore | grep -E "\.env|\.rdb|user_data"

# 4. Test Redis security
redis-cli CONFIG GET bind  # Should be 127.0.0.1 or localhost

# 5. Check disk space
df -h .
```

### Expected Output

```
============================================================
  MIGRU PRODUCTION READINESS CHECK
============================================================

✅ PASSED CHECKS:
   • Environment variables configured
   • Redis connection verified
   • API key security verified
   • Data privacy configuration verified

🎉 Ready for production!
```

## Running Migru

### Standard Usage

```bash
# Activate environment (if not already active)
source .venv/bin/activate

# Run Migru
uv run -m app.main
```

### As Installed Package

```bash
# After installation
migru
```

### With Custom Redis

```bash
# Start Redis on custom port
redis-server --port 6380

# Run Migru with custom Redis
REDIS_URL=redis://localhost:6380 uv run -m app.main
```

## Data Management

### User Data Location

All user data is stored in Redis:
- **Conversations**: `wellness_stream:{user_name}`
- **Profile**: `user_profile:{user_name}`
- **Patterns**: `patterns:{user_name}`
- **Memories**: Agno memory system in Redis

### Backup User Data

```bash
# Backup entire Redis database
redis-cli SAVE
cp /var/lib/redis/dump.rdb ~/migru-backup-$(date +%Y%m%d).rdb

# Or use Redis backup command
redis-cli BGSAVE
```

### Restore User Data

```bash
# Stop Redis
sudo systemctl stop redis

# Restore backup
sudo cp ~/migru-backup-20260111.rdb /var/lib/redis/dump.rdb
sudo chown redis:redis /var/lib/redis/dump.rdb

# Start Redis
sudo systemctl start redis
```

### Export User Data

```bash
# Export conversations
redis-cli --raw XRANGE wellness_stream:YourName - + > conversations.txt

# Export profile
redis-cli --raw GET user_profile:YourName > profile.json

# Export patterns
redis-cli --raw HGETALL patterns:YourName > patterns.txt
```

### Delete User Data

```bash
# Delete specific user
redis-cli DEL "user_profile:YourName"
redis-cli DEL "wellness_stream:YourName"
redis-cli DEL "patterns:YourName"

# Or delete all data
redis-cli FLUSHALL
```

## Monitoring

### Health Checks

```bash
# Check system health
python -c "
from app.production import HealthCheck
import json
health = HealthCheck.full_health_check()
print(json.dumps(health, indent=2))
"
```

### Monitor Redis

```bash
# Check Redis status
redis-cli INFO

# Monitor Redis in real-time
redis-cli --stat

# Check memory usage
redis-cli INFO memory

# List all keys (for debugging)
redis-cli KEYS "*"
```

### Check Logs

```bash
# Application logs (if configured)
tail -f logs/migru.log

# Redis logs
tail -f /var/log/redis/redis-server.log
```

## Troubleshooting

### Redis Connection Failed

```bash
# Check if Redis is running
redis-cli ping  # Should return "PONG"

# Start Redis
sudo systemctl start redis

# Or run manually
redis-server
```

### API Key Errors

```bash
# Verify environment variables
python -c "from app.config import config; print('Mistral:', bool(config.MISTRAL_API_KEY))"

# Check .env file exists
ls -la .env

# Verify .env is loaded
source .env && echo $MISTRAL_API_KEY
```

### Slow Performance

```bash
# Check which model is being used
# Cerebras is fastest, Mistral is fallback

# Verify Cerebras key is set
python -c "from app.config import config; print('Cerebras:', bool(config.CEREBRAS_API_KEY))"

# Check Redis memory
redis-cli INFO memory | grep used_memory_human

# Clear old data (optional)
redis-cli --scan --pattern "wellness_stream:*" | xargs redis-cli DEL
```

### Out of Disk Space

```bash
# Check disk usage
df -h .

# Check Redis database size
du -h /var/lib/redis/dump.rdb

# Clear old patterns
redis-cli --scan --pattern "patterns:*" | xargs redis-cli DEL

# Or flush all Redis data
redis-cli FLUSHALL
```

## Upgrading

### Update Migru

```bash
# Pull latest changes
git pull origin master

# Install updated dependencies
uv pip install -e .

# Run migration checks (if any)
python -m app.production
```

### Upgrade Dependencies

```bash
# Update all dependencies
uv pip install --upgrade -e .

# Or specific packages
uv pip install --upgrade agno redis pathway
```

## Privacy & Compliance

### GDPR Compliance

Migru is GDPR-compliant out of the box:
- ✅ **Data Minimization**: Only necessary data stored
- ✅ **Right to Erasure**: Easy deletion via Redis commands
- ✅ **Right to Access**: Easy export via Redis commands
- ✅ **Data Portability**: Standard Redis/JSON formats
- ✅ **Privacy by Design**: Local-first architecture

### Data Retention

Default retention periods:
- **Streaming events**: 30 days
- **User profile**: Persistent
- **Patterns**: 30 days
- **Memories**: Persistent

Configure retention in `app/services/realtime_analytics.py`:
```python
# Change retention period
self.redis_client.expire(pattern_key, 7 * 24 * 3600)  # 7 days
```

## Performance Tuning

### Optimize Redis

```bash
# Edit Redis config
sudo nano /etc/redis/redis.conf

# Recommended settings for Migru:
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

### Optimize Migru

```python
# In app/config.py

# Use fastest model
MODEL_PRIMARY = "cerebras:llama3.1-8b"

# Reduce history context
num_history_runs = 2  # In agents.py

# Disable features if not needed
ENABLE_STREAMING_ANALYTICS = False
ENABLE_PERSONALIZATION = False
```

## Security Best Practices

### 1. API Key Security
```bash
# Never commit .env
git rm --cached .env  # If accidentally added

# Use environment-specific keys
cp .env .env.production
cp .env .env.development

# Rotate keys regularly
```

### 2. Redis Security
```bash
# Bind to localhost only
redis-cli CONFIG SET bind "127.0.0.1"

# Require password (optional)
redis-cli CONFIG SET requirepass "your_strong_password"
```

### 3. File Permissions
```bash
# Secure .env file
chmod 600 .env

# Secure application
chmod 700 app/

# Check permissions
ls -la .env app/
```

### 4. Network Security
```bash
# Verify no external listeners
sudo netstat -tlnp | grep redis

# Should only show:
# 127.0.0.1:6379 (local only)
```

## Uninstallation

### Complete Removal

```bash
# 1. Stop Redis (if not used elsewhere)
sudo systemctl stop redis

# 2. Delete user data
redis-cli FLUSHALL

# 3. Remove application
rm -rf /path/to/migru

# 4. Remove virtual environment
rm -rf .venv

# 5. Uninstall Redis (optional)
sudo apt-get remove redis-server  # Ubuntu/Debian
brew uninstall redis              # macOS
```

### Keep User Data

```bash
# Backup before uninstalling
redis-cli SAVE
cp /var/lib/redis/dump.rdb ~/migru-data-backup.rdb

# Then uninstall
rm -rf /path/to/migru
```

## Support

### Getting Help

- **Documentation**: https://github.com/Ash-Blanc/migru#readme
- **Issues**: https://github.com/Ash-Blanc/migru/issues
- **Privacy**: See PRIVACY.md
- **Email**: angelash18092007@gmail.com

### Reporting Bugs

```bash
# Include system info
python -m app.production > system-info.txt

# Check health
python -c "from app.production import HealthCheck; print(HealthCheck.full_health_check())"
```

## Summary: Production Checklist

Before deploying for users:

- [ ] Run `python -m app.production` - all checks pass
- [ ] `.env` file has required API keys
- [ ] `.env` has `chmod 600` permissions
- [ ] Redis is running on localhost only
- [ ] `.gitignore` excludes `.env` and `*.rdb`
- [ ] Disk space >500MB available
- [ ] Backup strategy in place
- [ ] Privacy policy reviewed
- [ ] Security checklist completed

---

<div align="center">

**Deploy with confidence. Privacy first, always.**

*For questions: https://github.com/Ash-Blanc/migru/issues*

</div>
