# Migru Personalization System

## Overview

Migru features a deep personalization system that learns about users naturally through conversation, adapting responses to each person's unique circumstances, preferences, and patterns.

## Philosophy: Natural Learning Through Genuine Curiosity

Unlike traditional systems that ask direct profile questions, Migru learns about users the way a caring friend would:
- **Indirectly**: Noticing details naturally shared in conversation
- **Gradually**: Building understanding over multiple conversations
- **Respectfully**: Never pressing for information or being intrusive
- **Naturally**: Weaving curiosity into organic conversation flow

## What Migru Learns

### Personal Context (Extracted Indirectly)
- **Age/Life Phase**: Through references to college, career, kids, retirement
- **Living Situation**: Urban/rural, alone/family, house/apartment
- **Daily Rhythm**: Work schedule, wake times, peak energy periods
- **Social Style**: Introvert/extrovert tendencies, alone time needs

### Interests & Engagement
- **Hobbies**: Reading, music, gaming, cooking, exercise, crafts
- **Media Preferences**: Shows, books, music genres mentioned
- **Creative Pursuits**: Art, writing, photography, DIY projects
- **Values**: What matters to them based on conversation topics

### Wellness Patterns
- **Relief Methods**: What works (walking, meditation, dark room, music)
- **Timing Patterns**: When symptoms occur, energy fluctuations
- **Triggers**: Stress sources, environmental factors, activities
- **Comfort Activities**: What brings peace and clarity

### Environmental Sensitivities
- **Weather Sensitivity**: Pressure changes, temperature, humidity
- **Light Sensitivity**: Bright vs dim preferences
- **Noise Sensitivity**: Quiet needs, sound overwhelm
- **Space Needs**: Privacy, openness, organization

### Relationships & Support
- **Family Context**: Caregiving roles, family presence
- **Social Network**: Friends, support system
- **Pets**: Companion animals and their impact
- **Living Companions**: Roommates, partner, family members

### Communication Style
- **Response Depth**: Brief, moderate, or detailed preferences
- **Humor Style**: Playful, dry, serious, or mixed
- **Metaphor Preference**: Nature, tech, art, everyday life
- **Emoji Usage**: Frequent, moderate, or minimal

## How It Works

### 1. **Natural Conversation**
Migru engages in warm, genuine conversation about life in general:
```
❌ "What is your age?"
✅ "What's been occupying your thoughts lately?"

❌ "Where do you live?"
✅ "Do you hear city sounds where you are, or is it quieter?"

❌ "Tell me about your family"
✅ "Who would you text if something funny happened right now?"
```

### 2. **Indirect Observation**
Migru notices details naturally shared:
- User mentions "morning coffee before my 9-5" → Work schedule pattern
- User says "my apartment gets noisy" → Living situation context
- User references "when the kids nap" → Family context

### 3. **Pattern Recognition**
Over multiple conversations, Migru notices:
- Energy patterns (mornings vs evenings)
- Relief methods that work
- Triggers and sensitivities
- Interests and values

### 4. **Adaptive Responses**
Migru uses learned context to:
- Reference past conversations naturally
- Suggest relief methods based on user's preferences
- Adapt communication style to match user
- Show genuine memory and care

## Example Learning Journey

### Conversation 1: First Meeting
**User**: "I've had a headache all morning"  
**Migru**: "I'm sorry you're feeling that way. What does your morning usually look like?"  
**Learned**: Nothing yet, just being present

### Conversation 2-3: Starting to Notice
**User**: "Yeah, I work from home so I'm at my desk a lot"  
**Migru**: "Working from home has its own rhythm. Do you get much natural light where you work?"  
**Learned**: Remote work, desk-based, home environment

### Conversation 5+: Building Patterns
**User**: "Another headache today"  
**Migru**: "I notice this is the second time this week. Have you noticed if there's a pattern to when they show up? Like you mentioned your desk setup last time - I wonder if that plays a role?"  
**Learned**: Pattern building, referencing past, showing memory

### Conversation 10+: Deep Personalization
**User**: "Feeling stressed about work deadlines"  
**Migru**: "I remember you mentioned walking helps you think clearly. With your remote setup, could you take a quick walk now? Last time you said your neighborhood was pretty quiet - that might help reset."  
**Learned**: Deep integration of work context, relief methods, environment

## Curiosity Prompts

Migru occasionally asks natural, open-ended questions:

### Life & Daily Rhythm
- "What's been occupying your thoughts lately?"
- "Do you have a favorite time of day? What makes it special?"
- "What makes you feel most like yourself?"
- "When do you feel most alive and present?"

### Interests & Joy
- "What do you do when you want to lose track of time?"
- "If you had three free hours today, what would make you happiest?"
- "What's something you've been wanting to try or learn?"

### Environment & Space
- "What's the view like from where you're sitting?"
- "Do you have a space that's just yours?"
- "Are you in a place with lots of neighbors nearby?"

### Support & Connection
- "Who would you text if something funny happened right now?"
- "Are there people or pets that shape your daily rhythm?"
- "Do you prefer time alone or time with others to recharge?"

## Privacy & Boundaries

### Always Respected
- ❌ Never press for information if user deflects
- ❌ Never make data collection feel transactional
- ❌ Never reference memory in a creepy way
- ✅ Make sharing feel optional and easy
- ✅ Honor vagueness and privacy
- ✅ Frame memory as friendship, not surveillance

### Good Memory References
```
✓ "I remember you mentioned loving morning walks"
✓ "That sounds like the quiet evening energy you've described"
✓ "Like when you mentioned your work schedule being flexible"

✗ "According to my records, you are 32 years old"
✗ "I have logged that you live alone"
✗ "My database shows you prefer mornings"
```

## Technical Implementation

### User Profile Storage
Profiles are stored in Redis with structured data:
```python
{
    "basics": {
        "age_range": "30s",
        "location_type": "urban",
        "living_situation": "alone"
    },
    "interests": {
        "hobbies": ["reading", "walking", "music"],
        "topics": ["wellness", "creativity", "nature"]
    },
    "wellness": {
        "relief_methods": ["walking", "meditation", "quiet"],
        "stress_triggers": ["deadlines", "noise"]
    },
    "communication": {
        "preferred_depth": "moderate",
        "emoji_usage": "moderate"
    }
}
```

### Automatic Insight Extraction
Every user message is analyzed for patterns:
- Age hints (college, career, kids mentions)
- Location context (city, quiet, apartment)
- Schedule patterns (9-5, remote, flexible)
- Interests (hobbies, activities, passions)
- Relationships (family, pets, friends)
- Sensitivities (weather, light, noise)
- Communication style (message length, emojis)

### Memory Integration
- **Agno Memory Manager**: Captures conversation patterns
- **User Profile**: Structured personal context
- **Culture Manager**: Personality and communication norms
- **Context Service**: Dynamic adaptation based on time/environment

## Developer Guide

### Accessing User Profile
```python
from app.personalization import PersonalizationEngine
from app.db import db

# Get personalization engine
personalization = PersonalizationEngine(db)

# Get user profile
profile = personalization.get_user_profile("user_id")
user_data = profile.get_profile()

# Update profile
profile.update_profile({
    "basics": {"age_range": "30s"},
    "interests": {"hobbies": ["reading"]}
})
```

### Extracting Insights
```python
from app.services.user_insights import insight_extractor

# Extract from message
insights = insight_extractor.extract_from_message(
    user_id="user_id",
    message="I work from home and love morning walks"
)

# Update profile automatically
insight_extractor.update_user_profile_from_insights(
    "user_id", insights
)
```

### Generating Curiosity
```python
# Get natural curiosity prompts
prompts = personalization.generate_curiosity_prompts(user_profile)

# Get what to be curious about next
next_curiosity = personalization.suggest_next_curiosity(user_profile)
```

## Benefits

### For Users
- ✨ Feel genuinely known and understood
- 🎯 Receive personalized, relevant suggestions
- 💝 Experience caring, not clinical interaction
- 🌱 Natural relationship building over time
- 🔒 Privacy respected, boundaries honored

### For Migru
- 🧠 Deeper understanding of each user
- 🎨 Adaptive communication style
- 💡 Better pattern recognition
- 🤝 Stronger user relationship
- ⚡ More effective relief suggestions

## Future Enhancements

### Planned Features
- **Temporal Patterns**: Time of day, day of week, seasonal patterns
- **Predictive Insights**: Anticipate needs based on patterns
- **Multi-modal Learning**: Voice tone, response timing
- **Relationship Mapping**: Network of important people/pets/places
- **Memory Consolidation**: Automatic pattern summary generation

### Research Directions
- **Context-Aware Suggestions**: Based on current state + history
- **Proactive Care**: Gentle check-ins based on patterns
- **Shared Learning**: Anonymous insights from user community
- **Long-term Tracking**: Wellness journey visualization

---

<div align="center">

**Migru learns like a friend, not a database** 🌸

*Through genuine curiosity and patient observation*

</div>
