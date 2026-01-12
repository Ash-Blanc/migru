# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository for the DataQuest Hackathon.

## DataQuest Hackathon Focus

**Mission**: Create the most effective AI wellness companion for migraine and stress relief with real-time pattern detection.

**Competition Requirements** (from @dataquest.pdf):
- Real-time streaming analytics for wellness patterns
- Personalized agent behavior adaptation
- Multi-modal data integration (weather, time, user context)
- Low-latency response optimization
- Proactive wellness insights generation

## Development Commands

### Build & Install
```bash
# Install dependencies
uv sync

# Build the application
python -m pip install -e .

# Run with test environment
uv run -m app.main --user TestUser
```

### Linting & Quality
```bash
# Fast linting with ruff (optimized for speed)
ruff check app/

# Type checking
mypy app/ --ignore-missing-imports

# Format with black
black app/
```

### Testing
```bash
# Fast unit tests
pytest tests/ -v --tb=short

# Performance tests
pytest tests/ --performance

# Coverage with speed optimization
pytest tests/ --cov=app --cov-report=term-missing --cov-branch
```

### Development Server
```bash
# Start with verbose logging for debugging
uv run -m app.main --verbose

# Start with custom user for testing
uv run -m app.main --user "HackathonTester"
```

## High-Level Architecture (DataQuest Optimized)

### Core Components

1. **Real-Time Analytics Engine** (`app/services/realtime_analytics.py`)
   - PatternDetector: Redis Streams for low-latency event processing
   - InsightGenerator: Proactive wellness insights with 70% confidence threshold
   - Temporal pattern detection (hourly/daily rhythms)
   - Environmental correlation tracking (weather, pressure)

2. **AI Agent System** (`app/agents.py`)
   - Relief Team: Primary wellness-focused agent
   - Cerebras Team: High-speed backup (1000+ tokens/sec)
   - OpenRouter Team: Emergency fallback
   - SmartSearchTools: Multi-source search with automatic fallback

3. **Personalization Engine** (`app/personalization.py`)
   - Bio factor tracking (sleep, hydration, environment)
   - User preference adaptation
   - Contextual memory management
   - Adaptive communication style

4. **Streaming Infrastructure** (`app/streaming.py`)
   - Pathway integration for real-time data processing
   - Optimized message streaming with chunking
   - Live monitoring and event type extraction
   - Memory-efficient processing

### Key Files for Hackathon

- `app/main.py` - CLI interface with enhanced UX (command palette, live updates)
- `app/config.py` - Optimized model configuration for speed vs intelligence
- `app/memory.py` - Redis-based memory with culture and user profiles
- `app/tools.py` - Smart search with fallback mechanisms
- `app/utils.py` - Performance monitoring and memory optimization

## DataQuest-Specific Optimizations

### Performance Targets
- **Response Time**: <2 seconds for 90% of requests
- **Throughput**: 100+ concurrent users
- **Memory Usage**: <500MB baseline, efficient Redis usage
- **Latency**: Sub-second pattern detection updates

### Key Models (Speed Optimized)
```python
# Primary: Cerebras llama3.1-8b (blazing fast)
MODEL_PRIMARY = "cerebras:llama3.1-8b"

# Fallback: Mistral Small (quality + speed balance)
MODEL_SMART = "mistral:mistral-small-latest"

# Research: Fast research model
MODEL_RESEARCH = "mistral:mistral-small-latest"

# Emergency: OpenRouter Gemini Flash
MODEL_OPENROUTER_FALLBACK = "openrouter:google/gemini-2.0-flash-exp"
```

### Competition Features to Enhance

1. **Real-Time Pattern Detection**
   - Hourly symptom tracking
   - Weather correlation analysis
   - Time-based wellness insights
   - Proactive behavioral nudges

2. **Multi-Modal Integration**
   - Weather API integration
   - Time-based context awareness
   - User history correlation
   - Environmental factor tracking

3. **Agent Intelligence**
   - Personalized communication style
   - Context-aware responses
   - Proactive insight sharing
   - Adaptive learning from interactions

## Common Development Tasks

### 1. Adding Competition Features
```python
# Add new pattern detection
def add_new_pattern_detection():
    # 1. Update PatternDetector in realtime_analytics.py
    # 2. Add test in tests/services/test_realtime_analytics.py
    # 3. Update insight generation logic
    # 4. Test with realistic streaming data
```

### 2. Optimizing for Performance
```python
# Key optimization areas:
# 1. Reduce model context window usage
# 2. Optimize Redis queries with pipeline operations
# 3. Implement caching for weather data
# 4. Use streaming responses for long outputs
# 5. Minimize memory allocations in hot paths
```

### 3. Adding New Data Sources
```python
# Integration pattern:
# 1. Add new tool in app/tools.py
# 2. Update agent instructions in agents.py
# 3. Add pattern detection logic
# 4. Update configuration
# 5. Add comprehensive tests
```

### 4. Testing Competition Scenarios
```python
# Test real-time patterns
def test_real_time_pattern_detection():
    # Simulate high-frequency event streams
    # Test Redis performance under load
    # Validate insight generation timing
    # Test agent response latency
```

## Environment Setup for Competition

### Required API Keys (Set in .env)
```bash
# Essential for competition
MISTRAL_API_KEY=your_mistral_key
CEREBRAS_API_KEY=your_cerebras_key
OPENWEATHER_API_KEY=your_weather_key

# Optional but recommended
FIRECRAWL_API_KEY=your_firecrawl_key
OPENROUTER_API_KEY=your_openrouter_key
```

### Redis Setup
```bash
# Start Redis for local development
redis-server --daemonize yes

# Verify Redis is running
redis-cli ping  # Should return "PONG"
```

## Performance Monitoring

### Built-in Metrics
- Response time tracking
- Memory usage monitoring
- Redis connection health
- Model fallback frequency
- Pattern detection accuracy

### Key Performance Indicators
- **Latency**: 95th percentile < 2s
- **Availability**: 99.9% uptime target
- **Accuracy**: Pattern detection confidence > 70%
- **User Engagement**: Proactive insight acceptance rate

## Competition Strategy

### Phase 1: Core Stability
- Ensure all models work with fallback mechanisms
- Optimize Redis performance and memory usage
- Validate real-time pattern detection accuracy

### Phase 2: Feature Enhancement
- Add advanced weather correlation logic
- Implement time-based behavioral nudges
- Enhance personalization engine

### Phase 3: Performance Optimization
- Micro-optimize hot code paths
- Implement advanced caching strategies
- Fine-tune model selection for speed vs quality

### Phase 4: Polish & Testing
- Comprehensive load testing
- Real-world scenario validation
- User experience refinement

## Notes

- **Git Workflow**: Use feature branches for competition features
- **Code Style**: Follow Ruff configuration for consistency
- **Testing**: Always add tests for new competition features
- **Documentation**: Update README.md with competition-specific instructions
- **Monitoring**: Use built-in performance monitoring for optimization
- **Fallback Strategy**: Multiple model tiers ensure reliability under competition conditions

**Important**: Focus on real-time analytics, personalization, and low-latency responses for maximum competition impact.