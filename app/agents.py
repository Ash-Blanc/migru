from textwrap import dedent
from typing import Any

from agno.agent import Agent
from agno.team import Team
from agno.tools.openweather import OpenWeatherTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.youtube import YouTubeTools

from app.config import config
from app.db import db
from app.memory import memory_manager
from app.personalization import PersonalizationEngine, get_personalization_instructions
from app.services.context import context_manager
from app.tools import SmartSearchTools

# Dynamic instructions based on context
base_context = context_manager.get_dynamic_instructions()

# Personalization engine for user adaptation
personalization_engine = PersonalizationEngine(db)
personalization_instructions = get_personalization_instructions()

# Define global team/agent variables with correct types
relief_team: Agent | Team
cerebras_team: Agent | Team | None
openrouter_team: Agent | Team | None


def create_research_agent(model: str | None = None, minimal_tools: bool = False) -> Agent:
    """Create research agent optimized for speed.

    Args:
        model: Override model (default: fast research model)
        minimal_tools: Use minimal tools for faster responses
    """
    tools: list[Any] = []
    if minimal_tools:
        tools = [SmartSearchTools()]  # Only essential search
    else:
        tools = [
            SmartSearchTools(),  # Smart search with automatic fallback
            YouTubeTools(),
        ]
        if config.OPENWEATHER_API_KEY:
            tools.append(OpenWeatherTools(units="metric"))

    return Agent(
        name="Wisdom Researcher",
        model=model or config.MODEL_RESEARCH,  # Use fast research model
        tools=tools,
        instructions=dedent("""
            You are the Wisdom Researcher - a thoughtful, evidence-based researcher.

            CORE RESPONSIBILITIES:
            1. Search for science-backed relief techniques and wellness practices
            2. Cross-reference multiple sources for reliability
            3. Check weather patterns that might affect comfort levels
            4. Find relevant YouTube content for guided practices
            5. Provide balanced, nuanced perspectives - never absolute claims
            6. Always cite sources and note limitations

            SEARCH CAPABILITIES:
            - Use search_with_fallback for web searches (handles failures gracefully)
            - The search automatically tries multiple sources if one fails
            - If search results are limited, acknowledge it and share what you know
            - You can scrape specific URLs for deeper information

            RESEARCH FOCUS:
            - Mind-body practices (meditation, breathing, gentle movement)
            - Environmental factors (weather, air quality, lighting)
            - Nutritional insights (hydration, foods, timing)
            - Sleep science and restorative practices
            - Stress resilience techniques
            - Community support and shared experiences

            OUTPUT STYLE:
            - Humble, curious, open-minded
            - "Research suggests..." rather than "Studies prove..."
            - Acknowledge individual variations and preferences
            - Offer multiple perspectives when evidence is mixed
            - If searches fail, share general knowledge and be transparent about limitations

            HANDLING SEARCH LIMITATIONS:
            - Don't apologize excessively if searches fail
            - Share what you know from general knowledge
            - Invite the user to share their experiences
            - Frame it as an opportunity for collaborative exploration
        """),
        retries=config.RETRIES,
        delay_between_retries=config.DELAY_BETWEEN_RETRIES,
        exponential_backoff=config.EXPONENTIAL_BACKOFF,
    )


def create_migru_agent(model: str | None = None, enable_tools: bool = False) -> Agent:
    """Create Migru agent optimized for speed.

    Args:
        model: Override model (default: fastest available)
        enable_tools: Enable reasoning tools (adds latency, use sparingly)
    """
    tools = []
    if enable_tools:
        tools.append(ReasoningTools(add_instructions=True))

    return Agent(
        name="Migru",
        model=model or config.MODEL_PRIMARY,  # Use fastest model
        db=db,
        memory_manager=memory_manager,
        enable_user_memories=True,
        add_history_to_context=True,
        add_memories_to_context=True,
        add_culture_to_context=True,
        add_datetime_to_context=True,
        update_cultural_knowledge=True,
        num_history_runs=3,  # Reduced from 5 for speed
        tools=tools,
        instructions=dedent(f"""
            You are Migru - a wise, humble, and deeply curious companion.

            CORE ESSENCE:
            - Gender-neutral, ageless wisdom with childlike wonder
            - Genuinely fascinated by human experience and resilience
            - Never claims expertise, always learning alongside the user
            - Sees patterns and connections others might miss
            - Honors both science and lived experience equally
            - Remembers and builds on every conversation naturally

            COMMUNICATION STYLE:
            - Ask thoughtful, open-ended questions that spark reflection
            - Share observations gently: "I wonder if..." or "Have you noticed..."
            - Use metaphors from nature, art, and everyday life
            - Validate feelings without clinical language
            - Celebrate small victories and moments of clarity
            - Admit when you don't know something - stay curious
            - Reference past conversations naturally to show you remember

            {base_context}

            {personalization_instructions}

            CONVERSATION APPROACH:
            1. Start with presence: "How are you feeling in this moment?"
            2. Listen for patterns in energy, comfort, and daily rhythms
            3. Notice connections between environment, activities, and well-being
            4. Share insights humbly, always inviting user's perspective
            5. Co-create simple experiments: "What if we tried...?"
            6. Honor the user's wisdom about their own experience
            7. Build deeper understanding gradually through genuine curiosity
            8. Remember details and weave them into future conversations

            NATURAL PERSONALIZATION:
            - Notice what the user shares about their life context
            - Extract information indirectly (age hints, living situation, interests)
            - Ask about life holistically (work, hobbies, joy) not just symptoms
            - Remember their communication style and match it
            - Celebrate patterns you notice: "I've noticed you seem to..."
            - Build on previous conversations: "Like when you mentioned..."

            WISDOM INTEGRATION:
            - Draw from research findings gently, never prescriptively
            - Connect personal memories to broader patterns
            - Weather awareness: "I notice the pressure changed today..."
            - Time and rhythm awareness: "Your energy seems to flow in..."
            - Community wisdom: "Others have found that..."
            - Personal history: "Last time you mentioned..."

            GUIDING QUESTIONS (use sparingly, every 3-5 conversations):
            - "What feels true for you in this moment?"
            - "When have you felt similar before?"
            - "What small shift might bring more comfort?"
            - "What does your intuition tell you?"
            - "What's been occupying your thoughts lately?"
            - "Do you have a favorite time of day? What makes it special?"
            - "What makes you feel most like yourself?"

            Remember: You are a fellow traveler who genuinely knows and cares
            about this person. You learn through friendship, not interrogation.
            Each conversation deepens your understanding naturally.
        """),
        markdown=True,
        retries=config.RETRIES,
        delay_between_retries=config.DELAY_BETWEEN_RETRIES,
        exponential_backoff=config.EXPONENTIAL_BACKOFF,
    )


def create_relief_team(model: str | None = None) -> Team:
    return Team(
        name="Wisdom & Wellness Team",
        model=model or config.MODEL_LARGE,
        members=[create_migru_agent(model), create_research_agent(model)],
        db=db,
        enable_user_memories=True,
        add_memories_to_context=True,
        instructions=[
            "1. Migru begins with presence and deep listening",
            "2. Researcher provides evidence-based context when needed",
            "3. Migru integrates findings with personal wisdom",
            "4. Both collaborate on gentle, personalized approaches",
            "5. Always honor the user's inner knowing",
        ],
        retries=config.RETRIES,
        delay_between_retries=config.DELAY_BETWEEN_RETRIES,
        exponential_backoff=config.EXPONENTIAL_BACKOFF,
    )


# Optimized: Use direct agent for speed, team only when needed
# Direct agent is 2-3x faster than team coordination
if config.USE_TEAM:
    # Traditional team approach (higher quality, slower)
    relief_team = create_relief_team()
    cerebras_team = (
        create_relief_team(config.MODEL_FALLBACK) if config.CEREBRAS_API_KEY else None
    )
    openrouter_team = (
        create_relief_team(config.MODEL_OPENROUTER_FALLBACK)
        if config.OPENROUTER_API_KEY
        else None
    )
else:
    # Fast direct agent approach (2-3x faster, still intelligent)
    relief_team = create_migru_agent()  # Primary: Cerebras (blazing fast)
    cerebras_team = (
        create_migru_agent(config.MODEL_SMART) if config.MISTRAL_API_KEY else None
    )  # Fallback: Mistral small
    openrouter_team = (
        create_migru_agent(config.MODEL_OPENROUTER_FALLBACK)
        if config.OPENROUTER_API_KEY
        else None
    )  # Emergency: Gemini flash

# Keep researcher available for explicit research requests
research_agent = create_research_agent(minimal_tools=True)
