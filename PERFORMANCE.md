# Migru Performance Optimization Guide

## Overview
Migru is optimized for **low latency** while maintaining **high intelligence**. This guide explains the optimization strategies and how to tune them for your needs.

## Current Optimizations

### 1. **Model Selection Strategy** (Biggest Impact)

**Speed Hierarchy (fastest to slowest):**
1. ⚡ **Cerebras llama3.1-8b**: 1000+ tokens/sec (PRIMARY)
2. 🚀 **Mistral Small**: ~100-200 tokens/sec (FALLBACK)
3. 🌐 **Gemini 2.0 Flash**: ~150-300 tokens/sec (EMERGENCY)

**Current Configuration:**
```python
# Fast by default (Cerebras primary)
MODEL_PRIMARY = "cerebras:llama3.1-8b"       # ⚡ Blazing fast
MODEL_SMART = "mistral:mistral-small-latest" # 🚀 Fast + quality fallback
MODEL_RESEARCH = "mistral:mistral-small-latest"  # 🔍 Fast research
```

**Performance Impact:**
- Cerebras: ~1-2 second responses (typical)
- Mistral Small: ~3-5 second responses
- Mistral Medium: ~5-8 seconds
- Mistral Large: ~10-15 seconds

### 2. **Architecture: Direct Agent vs Team** (2-3x Faster)

**Current Mode: Direct Agent (Fast)**
```python
USE_TEAM = False  # Single agent, no coordination overhead
```

**Comparison:**
| Mode | Speed | Quality | Use Case |
|------|-------|---------|----------|
| Direct Agent | ⚡⚡⚡ | ⭐⭐⭐ | Most conversations (default) |
| Team | ⚡ | ⭐⭐⭐⭐ | Complex research requests |

**Why Direct is Faster:**
- No team coordination overhead
- No inter-agent communication
- Fewer model calls
- Direct response generation

**To Enable Team Mode (Higher Quality):**
```python
# In app/config.py
USE_TEAM = True  # Slower but more thorough
```

### 3. **Retry & Timeout Settings**

**Optimized for Speed:**
```python
RETRIES = 2  # Reduced from 3
DELAY_BETWEEN_RETRIES = 1  # Reduced from 2
EXPONENTIAL_BACKOFF = True  # Fast recovery
```

**Impact:** Faster failure recovery, less waiting on errors

### 4. **Context & History Management**

**Optimized Settings:**
```python
num_history_runs=3  # Reduced from 5 for speed
```

**Trade-offs:**
- Fewer history runs = faster processing
- Still maintains conversation context
- Balances memory and speed

### 5. **Streaming Responses**

**Enabled by Default:**
```python
STREAMING = True  # Show responses as they arrive
```

**Benefits:**
- Perceived speed improvement (instant feedback)
- Better user experience
- Actual speed unchanged but feels faster

### 6. **Tool Usage Optimization**

**Lazy-loaded Research:**
- Research agent only loaded when needed
- Minimal tools by default
- Smart fallback search reduces failures

**Tool Strategy:**
```python
# Migru: No tools by default (fastest)
# Research: Minimal tools (search only when needed)
# Full tools: Only on explicit research requests
```

### 7. **Logging Suppression**

**Silent Failures:**
- All verbose logs suppressed
- No visible error traces
- Clean, fast CLI experience

## Performance Tuning Guide

### For Maximum Speed (Current Setup)
```python
# config.py
MODEL_PRIMARY = "cerebras:llama3.1-8b"
USE_TEAM = False
RETRIES = 2
num_history_runs = 3  # In agents.py
```
**Expected:** 1-3 second responses

### For Best Quality (Slower)
```python
# config.py
MODEL_PRIMARY = "mistral:mistral-small-latest"
MODEL_SMART = "mistral:mistral-medium-latest"
USE_TEAM = True
RETRIES = 3
num_history_runs = 5
```
**Expected:** 5-10 second responses

### Balanced (Recommended for Most Users)
```python
# Current setup is already balanced!
# Cerebras primary, Mistral fallback
# Fast direct agent with quality fallback
```

## Monitoring Performance

### Enable Performance Metrics
```bash
uv run -m app.main --verbose
```

### Check Response Times
The app automatically tracks:
- Environment setup time
- CLI session duration
- Total startup time

### Troubleshooting Slow Responses

**If responses are slow (>5 seconds):**

1. **Check if Cerebras API key is set:**
   ```bash
   # In .env
   CEREBRAS_API_KEY=your_key_here
   ```

2. **Verify you're using direct agent mode:**
   ```python
   # In config.py
   USE_TEAM = False  # Should be False
   ```

3. **Check network latency:**
   ```bash
   # Test API response time
   curl -w "@curl-format.txt" -o /dev/null -s https://api.cerebras.ai
   ```

4. **Monitor Redis performance:**
   ```bash
   redis-cli ping  # Should return PONG instantly
   ```

5. **Reduce context size if needed:**
   ```python
   # In agents.py
   num_history_runs = 2  # Minimal history
   ```

## API Provider Speed Comparison

Based on real-world testing:

| Provider | Model | Speed | Cost | Quality |
|----------|-------|-------|------|---------|
| Cerebras | llama3.1-8b | ⚡⚡⚡⚡⚡ | $ | ⭐⭐⭐ |
| Mistral | mistral-small | ⚡⚡⚡ | $$ | ⭐⭐⭐⭐ |
| Mistral | mistral-medium | ⚡⚡ | $$$ | ⭐⭐⭐⭐ |
| OpenRouter | gemini-flash | ⚡⚡⚡ | $ | ⭐⭐⭐ |
| Mistral | mistral-large | ⚡ | $$$$ | ⭐⭐⭐⭐⭐ |

## Advanced Optimizations

### 1. Enable Cerebras as Primary
Make sure Cerebras is available and set as primary:
```bash
# .env
CEREBRAS_API_KEY=your_key_here
```

### 2. Reduce Memory Features (Minimal)
For absolute minimum latency:
```python
# In create_migru_agent()
enable_user_memories=False
add_history_to_context=False
add_memories_to_context=False
```
⚠️ **Warning:** Significantly reduces conversation quality

### 3. Disable Culture & Context (Not Recommended)
```python
add_culture_to_context=False
add_datetime_to_context=False
```
⚠️ **Warning:** Reduces personality and context awareness

### 4. Use Minimal Research Tools
```python
# In agents.py
research_agent = create_research_agent(minimal_tools=True)
```
✅ **Recommended:** Already enabled by default

## Benchmarking

### Test Response Speed
```bash
time uv run -m app.main <<EOF
Hello
How can you help with migraines?
exit
EOF
```

### Expected Results (with Cerebras)
- First response: 2-3 seconds
- Subsequent responses: 1-2 seconds
- Total conversation: <10 seconds

### Expected Results (with Mistral Small)
- First response: 4-6 seconds
- Subsequent responses: 3-5 seconds
- Total conversation: 15-20 seconds

## Summary

**Current Setup = Optimized for Speed & Quality**
- ⚡ Cerebras primary (1000+ tok/s)
- 🚀 Mistral Small fallback (quality)
- 🎯 Direct agent mode (2-3x faster)
- 📊 Smart tool usage (when needed)
- 🔄 Fast retry/fallback (1-2s)

**Result:** 1-3 second responses with high intelligence! 🌸
