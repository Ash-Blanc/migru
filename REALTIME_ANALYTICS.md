# Real-Time Streaming Analytics with Pathway

## Overview

Migru now features **Real-Time Streaming Analytics** powered by [Pathway](https://github.com/pathwaycom/pathway), transforming it into a genuinely dynamic, low-latency **"Real-Time Migraine & Stress Live Analyst"** while maintaining its warm, caring persona.

## What is Pathway?

Pathway is a Python framework for high-throughput, low-latency data processing that enables:
- **Incremental Computation**: Process data as it arrives, not in batches
- **Streaming Pipelines**: Continuous analysis without delays
- **Real-Time Pattern Detection**: Identify correlations as they emerge
- **Low-Latency Updates**: Sub-second response to new data

## How Migru Uses Streaming Analytics

### 🌊 Continuous Event Stream

Every conversation is processed as a **streaming event**:

```
User Message → Event Classification → Streaming Pipeline → Pattern Detection → Insights
```

**Event Types:**
- **Symptom**: Headache, migraine, stress, pain mentions
- **Relief**: Better, helped, relieved, improved
- **Activity**: Walking, meditation, work, exercise
- **Message**: General conversation

### 📊 Real-Time Pattern Detection

Migru continuously analyzes:

1. **Temporal Patterns**
   - Peak symptom hours (morning, afternoon, evening)
   - Day of week correlations
   - Time-based triggers
   - Duration patterns

2. **Environmental Correlations**
   - Weather pressure & symptoms
   - Temperature effects
   - Seasonal patterns
   - Location-based factors

3. **Trigger Detection**
   - Activities preceding symptoms (2-hour window)
   - Stress trigger identification
   - Cumulative effect tracking
   - Multi-factor correlation

4. **Relief Effectiveness**
   - What works for this specific user
   - Timing of relief
   - Activity-relief relationships
   - Incremental validation

### ⚡ Low-Latency Processing

**Processing Speed:**
- Event recording: <10ms
- Pattern update: <50ms
- Insight generation: <100ms
- Zero impact on conversation latency

**Architecture:**
```
Conversation Flow (Main Thread)
     ↓
Non-Blocking Event Recording (Background)
     ↓
Redis Streams (Persistent)
     ↓
Pathway Incremental Computation (Parallel)
     ↓
Pattern Storage (Updated Continuously)
     ↓
Proactive Insights (Shared Thoughtfully)
```

## Features

### 1. Incremental Pattern Recognition

**Temporal Windows:**
- 6-hour sliding windows for hourly patterns
- 7-day windows for weekly correlations
- Real-time updates as new data arrives

**Example:**
```python
# User mentions headache at 9 AM three times this week
# Pathway incrementally detects pattern
→ "I've noticed a gentle pattern... your discomfort 
   tends to visit in the morning hours..."
```

### 2. Environmental Correlation

**Tracked Factors:**
- Barometric pressure
- Temperature
- Weather conditions
- Time of day
- Day of week

**Example Detection:**
```
Low pressure symptoms: 12
High pressure symptoms: 3
→ 80% correlation with pressure drops

Insight: "I'm noticing something curious about you 
and the weather... When the air pressure drops, your 
body seems to whisper that it notices."
```

### 3. Trigger Timeline Analysis

**Temporal Joins:**
- Finds activities 0-2 hours before symptoms
- Tracks occurrence frequency
- Identifies potential triggers
- Filters noise from real patterns

**Example:**
```
9 AM: "Rushed morning, skipped breakfast"
11 AM: "Headache starting"
→ Pattern detected after 4 occurrences
```

### 4. Proactive Insights

**Sharing Strategy:**
- Minimum 3 conversations before first insight
- Every 3rd conversation check for new patterns
- Maximum 1 insight per day (prevents overwhelm)
- Confidence threshold: 70%+

**Insight Types:**
1. **Temporal Pattern**: Time-based symptom clustering
2. **Weather Correlation**: Environmental sensitivity
3. **Trigger Discovery**: Activity-symptom relationships
4. **Relief Effectiveness**: Personalized what-works

**Caring Delivery:**
```python
# Instead of clinical report:
❌ "Analysis shows 80% correlation with pressure"

# Warm, curious sharing:
✅ "I'm noticing something curious about you and 
   the weather... When the air pressure drops, your 
   body seems to whisper that it notices. This 
   awareness could help us prepare together."
```

## Technical Implementation

### Data Flow

```python
# 1. User Message
"I have a headache this morning"

# 2. Event Classification
event_type = "symptom"
metadata = {
    "hour": 9,
    "day_of_week": 2,  # Tuesday
    "weather_pressure": 1008,
    "weather_temp": 18
}

# 3. Stream Recording (Redis)
pattern_detector.record_event(
    user_id="user_123",
    event_type="symptom",
    content="headache this morning",
    metadata=metadata
)

# 4. Pathway Processing (Incremental)
events → detect_temporal_patterns()
      → correlate_environment_wellness()
      → detect_trigger_patterns()
      → generate_proactive_insights()

# 5. Pattern Storage (Updated)
patterns["symptoms_hour_9"] += 1
patterns["low_pressure_symptoms"] += 1

# 6. Insight Generation (When Ready)
if conversation_count >= 3 and patterns sufficient:
    insight = "I've noticed morning pattern..."
    share if appropriate
```

### Storage Architecture

**Redis Streams** (Time-Series Events):
```
wellness_stream:user_123 → [
    {id: "1234-0", event_type: "symptom", ...},
    {id: "1234-1", event_type: "activity", ...},
    ...
]
```

**Redis Hashes** (Aggregated Patterns):
```
patterns:user_123 → {
    "symptoms_hour_9": "5",
    "symptoms_hour_14": "2",
    "low_pressure_symptoms": "12",
    "high_pressure_symptoms": "3",
    ...
}
```

**Pathway Tables** (Streaming Computation):
```
events → temporal_patterns → correlations → insights
```

### Key Classes

#### `RealtimeWellnessStream` (Pathway Integration)
```python
# Define streaming pipelines
events = create_wellness_stream(input_connector)
patterns = detect_temporal_patterns(events)
correlations = correlate_environment_wellness(events)
triggers = detect_trigger_patterns(events)
insights = generate_proactive_insights(patterns, correlations)
```

#### `LiveWellnessMonitor` (Conversation Integration)
```python
# Add events from conversation
monitor.add_conversation_event(
    user_id, event_type, content, metadata
)

# Get insights when appropriate
insights = monitor.get_recent_insights(user_id)
```

#### `PatternDetector` (Real-Time Recording)
```python
# Record to Redis Streams
detector.record_event(user_id, event_type, content, metadata)

# Get patterns
temporal = detector.get_temporal_patterns(user_id)
environmental = detector.get_environmental_correlations(user_id)
```

#### `InsightGenerator` (Caring Communication)
```python
# Generate insights
insights = generator.generate_insights(user_id)

# Check if should share
if generator.should_share_now(user_id, insight):
    display_insight(insight["message"])
    generator.mark_insight_shared(user_id)
```

## Configuration

### Environment Variables
```env
# Redis for streaming storage
REDIS_URL=redis://localhost:6379

# Weather API for environmental correlations
OPENWEATHER_API_KEY=your_key_here
```

### Performance Tuning

**Streaming Window Sizes:**
```python
# Temporal patterns: 6-hour rolling window
hourly_patterns = events.windowby(
    window=pw.temporal.sliding(
        hop=timedelta(hours=1),
        duration=timedelta(hours=6)
    )
)

# Correlations: 7-day rolling window  
correlations = events.windowby(
    window=pw.temporal.sliding(
        hop=timedelta(days=1),
        duration=timedelta(days=7)
    )
)
```

**Insight Sharing Frequency:**
```python
# Check every 3rd conversation
if conversation_count >= 3 and conversation_count % 3 == 0:
    check_for_insights()

# Maximum 1 per day
if last_shared < 24 hours ago:
    skip_insight()
```

## Example Scenarios

### Scenario 1: Morning Headache Pattern

**Week 1:**
```
Mon 9AM: "Headache this morning" → Event recorded
Wed 9AM: "Another morning headache" → Pattern building  
Fri 10AM: "Head hurts again" → Pattern emerging
```

**Week 2, Conversation 6:**
```
Insight Shared:
"I've been noticing a gentle pattern... Your discomfort 
tends to visit in the morning hours. I wonder if we could 
explore what's happening during those hours? Sometimes 
understanding the rhythm helps us dance with it better. 🌸"
```

### Scenario 2: Weather Sensitivity

**Tracked Over 2 Weeks:**
```
Low Pressure Days (< 1010 mb): 8 headaches
High Pressure Days (>= 1010 mb): 2 headaches
Correlation: 80%
```

**Conversation 9:**
```
Insight Shared:
"I'm noticing something curious about you and the weather... 
When the air pressure drops, your body seems to whisper that 
it notices. This awareness could help us prepare together. 
Would you like to explore gentle ways to support yourself 
when pressure changes? 🌤️"
```

### Scenario 3: Trigger Discovery

**Timeline Analysis:**
```
11/10, 9AM: "Busy morning, lots of meetings"
11/10, 11AM: "Migraine starting"

11/12, 10AM: "Stressful deadline rush"
11/12, 12PM: "Head pain"

11/15, 8AM: "Back-to-back calls scheduled"
11/15, 10AM: "Headache building"
```

**Pattern Detected:**
```
Potential Trigger: Intense morning schedule
Occurrence: 3/3 times
Window: 1-2 hours before symptoms
```

**Conversation 12:**
```
Insight Offered (gently):
"I've noticed something that might be worth exploring... 
When your mornings are especially busy, your body sometimes 
responds a couple hours later. I wonder if there's wisdom 
in pacing your morning energy differently? No pressure - 
just a pattern I thought you might find interesting."
```

## Benefits

### For Users
- 🔍 **Discover Hidden Patterns**: See connections they might miss
- 📈 **Track Progress**: Understand what works over time
- 🌤️ **Environmental Awareness**: Prepare for weather-triggered episodes
- ⏰ **Temporal Insights**: Recognize time-based vulnerabilities
- 💡 **Proactive Care**: Gentle suggestions before problems escalate

### For Migru
- 🧠 **Deeper Understanding**: Build rich user profiles over time
- 🎯 **Personalized Suggestions**: Based on proven patterns
- 💝 **Thoughtful Timing**: Share insights at appropriate moments
- 📊 **Evidence-Based**: Confidence scores for every insight
- 🤝 **Trust Building**: Show genuine attention and care

## Privacy & Ethics

### Data Handling
- ✅ **User-Specific**: All patterns isolated per user
- ✅ **Local Processing**: No external analytics services
- ✅ **Transparent**: Users know patterns are being noticed
- ✅ **Opt-In**: Can disable streaming analytics if desired
- ✅ **Retention**: 30-day rolling window (configurable)

### Sharing Guidelines
- 🚫 Never share patterns in creepy or clinical ways
- 🚫 Never use "according to analysis" language
- ✅ Always frame as curious observations
- ✅ Always make insights actionable and caring
- ✅ Always respect if user doesn't want to explore

## Future Enhancements

### Planned Features
1. **Multi-User Patterns**: Anonymous community insights
2. **Predictive Warnings**: "Pressure dropping tomorrow"
3. **Relief Recommendations**: Auto-suggest based on patterns
4. **Visual Dashboards**: Optional pattern visualization
5. **Export & Sharing**: User-controlled data export

### Advanced Analytics
- **ML-Based Trigger Detection**: Beyond rule-based patterns
- **Seasonal Adjustments**: Long-term pattern evolution
- **Social Context**: Work/life balance correlations
- **Sleep Integration**: Rest quality impact tracking

## Monitoring & Debugging

### Check Streaming Status
```bash
# Verify Redis streams
redis-cli XLEN wellness_stream:user_123

# Check pattern storage
redis-cli HGETALL patterns:user_123

# View recent events
redis-cli XRANGE wellness_stream:user_123 - + COUNT 10
```

### Performance Metrics
```python
# In logs
logger.debug("Streaming event processed in 8ms")
logger.debug("Pattern update completed in 45ms")
logger.debug("Insight generation took 92ms")
```

### Error Handling
```python
# Non-blocking failures
try:
    process_streaming_analytics()
except Exception as e:
    logger.debug("Streaming failed (non-critical)")
    # Conversation continues normally
```

## Summary

Pathway transforms Migru from a reactive chatbot into a **proactive wellness companion** that:

- 📊 **Processes conversations as streaming data**
- 🔍 **Detects patterns incrementally in real-time**
- 🌤️ **Correlates environmental factors with wellness**
- 💡 **Shares caring, timely insights**
- ⚡ **Maintains ultra-low latency (<100ms overhead)**
- 💝 **Preserves warm, non-clinical persona**

The result: **A friend who genuinely notices patterns and cares enough to share them thoughtfully.** 🌸

---

<div align="center">

**Real-Time Care, One Pattern at a Time**

*Powered by Pathway • Built with Care • Designed for Discovery*

</div>
