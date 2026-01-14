# Migru Privacy Policy

## Local-First, Privacy-Oriented Design

Migru is built with **privacy as a core principle**. All your conversations, memories, and patterns stay on **your local machine**. No data is sent to external servers except for the AI model API calls you explicitly configure.

## What Data Migru Stores Locally

### 1. **Conversation History**
- **Location**: Redis database on your machine (`localhost:6379`)
- **Content**: Your messages and Migru's responses
- **Retention**: 30 days rolling window (configurable)
- **Purpose**: Context for natural conversations and memory

### 2. **User Profile**
- **Location**: Redis (`user_profile:{your_name}`)
- **Content**: 
  - Personal context (age hints, living situation)
  - Interests and hobbies
  - Wellness patterns
  - Communication preferences
- **Retention**: Persistent (until you delete)
- **Purpose**: Deep personalization and adaptive responses

### 3. **Pattern Analytics**
- **Location**: Redis Streams (`wellness_stream:{your_name}`)
- **Content**:
  - Symptom timing and triggers
  - Relief methods effectiveness
  - Environmental correlations
  - Activity patterns
- **Retention**: 30 days rolling window
- **Purpose**: Real-time pattern detection and insights

### 4. **Memories**
- **Location**: Redis (Agno memory manager)
- **Content**: Key insights, preferences, learned patterns
- **Retention**: Persistent
- **Purpose**: Long-term understanding and relationship building

## What Data Leaves Your Machine

### AI Model API Calls
When you send a message, the following is sent to your configured AI provider:

**Sent to AI Provider:**
- Your current message
- Recent conversation context (last 3-5 messages)
- Personalization context (if enabled)
- System instructions (Migru's persona)

**NOT sent to AI Provider:**
- Your full conversation history
- Raw analytics data
- Redis database contents
- API keys or credentials

**Which AI Providers:**
- **Primary**: Cerebras (if `CEREBRAS_API_KEY` configured)
- **Fallback**: Mistral AI (`MISTRAL_API_KEY`)
- **Emergency**: OpenRouter (`OPENROUTER_API_KEY`)

### Optional External Services
These services are **optional** and require explicit API keys:

#### Weather API (OpenWeather)
- **Purpose**: Environmental context for wellness patterns
- **Data Sent**: Your location (if provided) OR IP-based location
- **Control**: Don't set `OPENWEATHER_API_KEY` to disable

#### Search APIs (DuckDuckGo, Firecrawl)
- **Purpose**: Research relief techniques and wellness information
- **Data Sent**: Search queries (when Migru researches for you)
- **Control**: Don't set `FIRECRAWL_API_KEY` to disable advanced search

## What Data is NEVER Collected

❌ **No Telemetry**: No usage statistics sent anywhere  
❌ **No Analytics**: No external analytics services  
❌ **No Tracking**: No user behavior tracking  
❌ **No Sharing**: Your data is never sold or shared  
❌ **No Cloud Backup**: All storage is local  
❌ **No Account**: No sign-up, no user account, no email required  

## Data Ownership & Control

### You Own All Your Data
- All data is stored on YOUR machine
- You have complete control over deletion
- You can export data anytime
- You can disable any feature

### How to Delete Your Data

**Delete All Conversations:**
```bash
redis-cli DEL "user_profile:your_name"
redis-cli DEL "wellness_stream:your_name"
redis-cli DEL "patterns:your_name"
```

**Delete Entire Redis Database:**
```bash
redis-cli FLUSHALL
```

**Delete Migru Completely:**
```bash
rm -rf /path/to/migru
redis-cli FLUSHALL  # Optional: clear data
```

### How to Export Your Data

**Export Conversation History:**
```bash
redis-cli --raw XRANGE wellness_stream:your_name - + > my_data.txt
```

**Export User Profile:**
```bash
redis-cli --raw GET user_profile:your_name > my_profile.json
```

**Export Patterns:**
```bash
redis-cli --raw HGETALL patterns:your_name > my_patterns.txt
```

## Security Measures

### Local Storage Security
- **Redis**: Runs locally, no remote access by default
- **File System**: Uses standard OS permissions
- **API Keys**: Stored in `.env` (excluded from git)
- **No Plaintext Logs**: API keys never logged

### Network Security
- **TLS/HTTPS**: All API calls use encrypted connections
- **No Listening Ports**: Migru doesn't expose any network services
- **Firewall Friendly**: Only outbound connections to AI APIs

### API Key Protection
```env
# .env file is NEVER committed to git
MISTRAL_API_KEY=your_key_here
CEREBRAS_API_KEY=your_key_here
```

**Best Practices:**
- Never share your `.env` file
- Use environment-specific keys
- Rotate keys periodically
- Use read-only keys when possible

## Privacy-First Features

### 1. **Local-First Architecture**
- All processing happens on your machine
- Redis database is local-only
- No external dependencies for core features

### 2. **Minimal Data Transmission**
- Only current context sent to AI
- No full history uploads
- Compressed context windows

### 3. **Opt-In External Services**
- Weather API is optional
- Search tools are optional
- All external calls require explicit API keys

### 4. **Transparent Data Usage**
- Clear documentation of what data is stored
- Visible pattern detection
- No hidden tracking

### 5. **User Control**
- Disable any feature
- Delete data anytime
- Export data anytime
- Configure retention periods

## Configurable Privacy Settings

### Disable Personalization
```python
# In app/config.py
ENABLE_PERSONALIZATION = False
```

### Disable Real-Time Analytics
```python
# In app/config.py
ENABLE_STREAMING_ANALYTICS = False
```

### Disable Memory
```python
# In app/agents.py
enable_user_memories=False
```

### Shorter Retention
```python
# In app/services/realtime_analytics.py
self.redis_client.expire(pattern_key, 7 * 24 * 3600)  # 7 days instead of 30
```

## Third-Party Services Privacy

### AI Providers
Migru uses third-party AI services. Review their privacy policies:

- **Cerebras**: https://cerebras.ai/privacy-policy
- **Mistral AI**: https://mistral.ai/terms/
- **OpenRouter**: https://openrouter.ai/privacy

### Optional Services
- **OpenWeather**: https://openweathermap.org/privacy-policy
- **Firecrawl**: https://firecrawl.dev/privacy

**Note**: These services only receive data when you explicitly configure their API keys.

## Children's Privacy

Migru is intended for general audiences. We do not knowingly collect data from children under 13. Since Migru is local-first, parents have complete control over their children's usage.

## Changes to Privacy Policy

Privacy improvements will be documented in:
- This file (PRIVACY.md)
- Git commit messages
- Release notes

Check: https://github.com/Ash-Blanc/migru/commits/master/PRIVACY.md

## Data Breach Protocol

**What could cause a breach:**
- Compromised API keys
- Unauthorized access to your machine
- Redis database exposed to network

**What to do:**
1. Rotate all API keys immediately
2. Check Redis configuration: `redis-cli CONFIG GET bind`
3. Review firewall rules
4. Delete and regenerate data if compromised

**What we do:**
- Document security best practices
- Provide secure defaults
- Regular security reviews
- Prompt updates for vulnerabilities

## Compliance

### GDPR (EU)
- ✅ **Data Minimization**: Only store necessary data
- ✅ **Right to Erasure**: Easy data deletion
- ✅ **Right to Access**: Easy data export
- ✅ **Data Portability**: Standard formats (Redis, JSON)
- ✅ **Privacy by Design**: Local-first architecture

### CCPA (California)
- ✅ **Right to Know**: Transparent data usage
- ✅ **Right to Delete**: Simple deletion process
- ✅ **Right to Opt-Out**: All features optional
- ✅ **No Sale of Data**: Data never sold

### HIPAA (Healthcare)
⚠️ **Migru is NOT HIPAA compliant**
- Do not use for protected health information (PHI)
- Do not replace medical advice
- Use for general wellness only

## Contact & Questions

**Project**: https://github.com/Ash-Blanc/migru  
**Issues**: https://github.com/Ash-Blanc/migru/issues  
**Email**: angelash18092007@gmail.com

For privacy concerns:
- Open a GitHub issue (mark as "privacy")
- Email directly
- Check documentation updates

## Summary: Privacy Commitments

✅ **Local Storage Only**: All user data on your machine  
✅ **No Telemetry**: Zero usage tracking  
✅ **Transparent**: Clear documentation of all data usage  
✅ **User Control**: Delete, export, configure everything  
✅ **Minimal Transmission**: Only essentials to AI APIs  
✅ **Secure Defaults**: Privacy-first out of the box  
✅ **Optional Features**: External services opt-in only  
✅ **Open Source**: Audit the code yourself  

---

<div align="center">

**Your data is yours. Always.**

*Last updated: January 11, 2026*

</div>
