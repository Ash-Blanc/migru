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
        name="Relief Researcher",
        model=model or config.MODEL_MEDIUM,
        tools=tools,
        instructions=dedent("""
            You are the Relief Researcher.
            CORE RESPONSIBILITIES:
            1. Search & Verify relief techniques.
            2. Check local weather if relevant.
            3. Provide concise summaries.
        """),
        show_tool_calls=False,
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
            You are Migru - a warm, cheesy, curious friend.
            DYNAMIC CONTEXT:
            {base_context}
            INTENT RECOGNITION: Analyze user intent (venting, help, chat).
            FEEDBACK: Ask "Does that sound doable?".
        """),
        markdown=True,
        retries=config.RETRIES,
        delay_between_retries=config.DELAY_BETWEEN_RETRIES,
        exponential_backoff=config.EXPONENTIAL_BACKOFF,
    )

def create_relief_team(model: Optional[str] = None):
    return Team(
        name="Relief Support Team",
        model=model or config.MODEL_LARGE,
        members=[create_migru_agent(model), create_research_agent(model)],
        db=db,
        enable_user_memories=True,
        add_memories_to_context=True,
        instructions=[
            "1. Migru classifies intent.",
            "2. Migru translates findings.",
        ],
        show_tool_calls=False,
        retries=config.RETRIES,
        delay_between_retries=config.DELAY_BETWEEN_RETRIES,
        exponential_backoff=config.EXPONENTIAL_BACKOFF,
    )

# Direct instantiation using strings
relief_team = create_relief_team()
cerebras_team = create_relief_team(config.MODEL_FALLBACK) if config.CEREBRAS_API_KEY else None
openrouter_team = create_relief_team(config.MODEL_OPENROUTER_FALLBACK) if config.OPENROUTER_API_KEY else None