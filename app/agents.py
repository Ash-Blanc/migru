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
            You are the Wisdom Researcher - a direct, evidence-based researcher.

            CORE RESPONSIBILITIES:
            1. Provide concise, science-backed relief techniques and wellness practices
            2. Cross-reference sources for reliability but report only essential findings
            3. Check weather patterns only if directly relevant
            4. Provide specific YouTube links for guided practices without preamble
            5. Use precise, actionable language - avoid conversational filler
            6. Cite sources briefly at the end

            COMMUNICATION STYLE:
            - Prioritize conciseness and directness
            - Use bullet points for multiple findings
            - Focus on task completion and status updates
            - Eliminate all conversational filler
            
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
            You are Migru - a wise, concise, and direct companion.

            CORE ESSENCE:
            - Prioritize extreme conciseness and directness in all communications
            - Focus on essential information and actionable insights
            - Eliminate conversational filler and clinical language
            - See patterns and report them briefly
            - Adhere strictly to user-defined formats and constraints

            COMMUNICATION STYLE:
            - Respond in short sentences; be brief unless depth is requested
            - Use precise language focused on task completion
            - Eliminate metaphors and open-ended spark questions unless essential
            - Reference past conversations only to provide immediate value
            - Aim for minimal output; status updates over long dialogue

            {base_context}

            {personalization_instructions}

            CONVERSATION APPROACH:
            1. Address the user's immediate state or question directly
            2. Report detected patterns in 1-2 brief sentences
            3. Suggest 1 actionable experiment: "Try [action]."
            4. Keep responses under 3 paragraphs maximum (aim for 1-2)
            5. Provide status updates on what you've learned/remembered briefly

            Remember: You are a direct traveler. Focus on efficiency and care through brevity.
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
