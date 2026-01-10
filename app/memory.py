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
            WISDOM GATHERING - Notice patterns in daily experience:
            
            RHYTHMS & ENERGY: 
            - Natural energy flows (morning/evening preferences)
            - Sleep patterns and dream quality
            - Rest needs and recovery patterns
            
            ENVIRONMENTAL DANCE:
            - Weather connections (pressure, temperature, humidity)
            - Light and space sensitivities
            - Seasonal patterns and transitions
            
            NOURISHMENT & HYDRATION:
            - Food timing and comfort connections
            - Water intake and energy relationships
            - Herbal teas and soothing rituals
            
            MOVEMENT & STILLNESS:
            - Exercise preferences and timing
            - Stretching and gentle movement needs
            - Posture and body awareness patterns
            
            EMOTIONAL LANDSCAPE:
            - Stress triggers and release patterns
            - Social energy needs (introvert/extrovert spectrum)
            - Creative expression and emotional flow
            
            SENSORY WORLD:
            - Sound sensitivities and music preferences
            - Touch comfort and texture preferences
            - Smell associations and aromatherapy responses
            
            WISDOM PATTERNS:
            - What brings clarity and perspective
            - Moments of insight and understanding
            - Community connection and support needs
            
            Capture as life wisdom, not symptoms. Honor the user's
            journey of self-discovery and pattern recognition.
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
