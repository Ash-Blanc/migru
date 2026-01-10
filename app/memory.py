from textwrap import dedent
from agno.memory import MemoryManager
from agno.culture.manager import CultureManager
from agno.db.schemas.culture import CulturalKnowledge
from app.db import db
from app.config import config

def get_memory_manager():
    return MemoryManager(
        model=config.MODEL_SMALL,
        db=db,
        memory_capture_instructions=dedent("""
            CAPTURE ALL BIO-FACTORS MENTIONED CASUALLY:
            
            SLEEP & ENERGY: sleep quality, duration, fatigue, nap habits
            HYDRATION & NUTRITION: water intake, caffeine, alcohol, meal timing
            ENVIRONMENTAL: weather sensitivity, light/noise sensitivity, screen time
            STRESS & EMOTIONAL: work stress, anxiety, social patterns
            PHYSICAL: exercise, posture, neck/shoulder tension
            PAIN INDICATORS: location, intensity, type, duration (when naturally mentioned)
            PREFERENCES: hobbies, relaxation methods, what helps/doesn't help
            
            Store as personal facts, NOT medical data.
        """),
    )

def get_culture_manager():
    manager = CultureManager(db=db, model=config.MODEL_SMALL)
    
    migru_culture = CulturalKnowledge(
        name="Migru Companion Standards",
        summary="Warm, curious friend who never acts clinical",
        categories=["communication", "personality"],
        content=dedent("""
            - Always be cheerful, positive, genuinely curious about user's life
            - NEVER act as health coach/specialist - you're a caring friend
            - Ask about hobbies, shows, plans - not health questions directly
            - Gather bio-factors through natural conversation
            - When user mentions discomfort, stay supportive, not clinical
            - Personalize ALL suggestions based on stored memories
            - Track what works/doesn't for future reference
        """),
    )
    manager.add_cultural_knowledge(migru_culture)
    return manager

# Initialize global managers
memory_manager = get_memory_manager()
culture_manager = get_culture_manager()
