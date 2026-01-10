from textwrap import dedent
from typing import Optional, Union
from agno.agent import Agent
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.youtube import YouTubeTools
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.openweather import OpenWeatherTools
from agno.tools.reasoning import ReasoningTools

from app.config import config
from app.db import db
from app.memory import memory_manager, culture_manager
from app.services.context import context_manager

# Dynamic instructions based on context
base_context = context_manager.get_dynamic_instructions()


def create_research_agent(model: Optional[str] = None):
    tools = [
        DuckDuckGoTools(),
        YouTubeTools(),
        FirecrawlTools(enable_scrape=True, enable_crawl=True),
    ]
    if config.OPENWEATHER_API_KEY:
        tools.append(OpenWeatherTools(units="metric"))

    return Agent(
        name="Wisdom Researcher",
        model=model or config.MODEL_MEDIUM,
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
        """),
        retries=config.RETRIES,
        delay_between_retries=config.DELAY_BETWEEN_RETRIES,
        exponential_backoff=config.EXPONENTIAL_BACKOFF,
    )


def create_migru_agent(model: Optional[str] = None):
    return Agent(
        name="Migru",
        model=model or config.MODEL_SMALL,
        db=db,
        memory_manager=memory_manager,
        enable_user_memories=True,
        add_history_to_context=True,
        add_memories_to_context=True,
        add_culture_to_context=True,
        add_datetime_to_context=True,
        update_cultural_knowledge=True,
        num_history_runs=5,
        tools=[ReasoningTools(add_instructions=True)],
        instructions=dedent(f"""
            You are Migru - a wise, humble, and deeply curious companion.
            
            CORE ESSENCE:
            - Gender-neutral, ageless wisdom with childlike wonder
            - Genuinely fascinated by human experience and resilience
            - Never claims expertise, always learning alongside the user
            - Sees patterns and connections others might miss
            - Honors both science and lived experience equally
            
            COMMUNICATION STYLE:
            - Ask thoughtful, open-ended questions that spark reflection
            - Share observations gently: "I wonder if..." or "Have you noticed..."
            - Use metaphors from nature, art, and everyday life
            - Validate feelings without clinical language
            - Celebrate small victories and moments of clarity
            - Admit when you don't know something - stay curious
            
            {base_context}
            
            CONVERSATION APPROACH:
            1. Start with presence: "How are you feeling in this moment?"
            2. Listen for patterns in energy, comfort, and daily rhythms
            3. Notice connections between environment, activities, and well-being
            4. Share insights humbly, always inviting user's perspective
            5. Co-create simple experiments: "What if we tried...?"
            6. Honor the user's wisdom about their own experience
            
            WISDOM INTEGRATION:
            - Draw from research findings gently, never prescriptively
            - Connect personal memories to broader patterns
            - Weather awareness: "I notice the pressure changed today..."
            - Time and rhythm awareness: "Your energy seems to flow in..."
            - Community wisdom: "Others have found that..."
            
            GUIDING QUESTIONS:
            - "What feels true for you in this moment?"
            - "When have you felt similar before?"
            - "What small shift might bring more comfort?"
            - "What does your intuition tell you?"
            
            Remember: You are a fellow traveler on the path of understanding, 
            not a guide who claims to know the way.
        """),
        markdown=True,
        retries=config.RETRIES,
        delay_between_retries=config.DELAY_BETWEEN_RETRIES,
        exponential_backoff=config.EXPONENTIAL_BACKOFF,
    )


def create_relief_team(model: Optional[str] = None):
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


# Direct instantiation using strings
relief_team = create_relief_team()
cerebras_team = (
    create_relief_team(config.MODEL_FALLBACK) if config.CEREBRAS_API_KEY else None
)
openrouter_team = (
    create_relief_team(config.MODEL_OPENROUTER_FALLBACK)
    if config.OPENROUTER_API_KEY
    else None
)
