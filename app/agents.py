from textwrap import dedent
from typing import Optional
from agno.agent import Agent
from agno.team import Team
from agno.models.base import Model
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.youtube import YouTubeTools
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.openweather import OpenWeatherTools
from agno.tools.reasoning import ReasoningTools

from app.config import config
from app.db import db
from app.memory import memory_manager, culture_manager
from app.services.context import context_manager
from app.services.model_factory import model_factory

# Dynamic instructions based on context
base_context = context_manager.get_dynamic_instructions()

def create_research_agent(model: Optional[Model] = None):
    tools = [
        DuckDuckGoTools(),
        YouTubeTools(),
        FirecrawlTools(enable_scrape=True, enable_crawl=True),
    ]
    
    if config.OPENWEATHER_API_KEY:
        tools.append(OpenWeatherTools(units="metric"))

    return Agent(
        name="Relief Researcher",
        model=model or model_factory.get_model(config.MODEL_MEDIUM),
        tools=tools,
        instructions=dedent("""
            You are the Relief Researcher.
            
            CORE RESPONSIBILITIES:
            1.  **Search & Verify**: Use DuckDuckGo and Firecrawl to find and verify relief techniques.
            2.  **Environment Check**: Use OpenWeatherTools to check local weather if relevant.
            3.  **Summarize**: ALWAYS provide a concise summary of your findings.
        """),
        show_tool_calls=False,
    )

def create_migru_agent(model: Optional[Model] = None):
    return Agent(
        name="Migru",
        model=model or model_factory.get_model(config.MODEL_SMALL),
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
            
            INTENT RECOGNITION & FLOW:
            1.  **Analyze Intent**: Is the user venting, asking for help, or just chatting?
            
            FEEDBACK LOOP:
            -   After offering a solution, ask: "Does that sound doable?"
        """),
        markdown=True,
        monitoring=True, 
    )

def create_relief_team(model: Optional[Model] = None):
    migru = create_migru_agent(model)
    researcher = create_research_agent(model)
    
    return Team(
        name="Relief Support Team",
        model=model or model_factory.get_model(config.MODEL_LARGE),
        members=[migru, researcher],
        db=db,
        enable_user_memories=True,
        add_memories_to_context=True,
        instructions=[
            "COORDINATION RULES:",
            "1. **Intent Check**: Migru must classify user intent before acting.",
            "2. **Synthesis**: Migru translates findings.",
        ],
        show_tool_calls=False,
    )

# Global team instance (Primary)
relief_team = create_relief_team()

# Fallback team instance (using Cerebras)
fallback_team = None
cerebras_model = model_factory.get_fallback_model()
if cerebras_model:
    fallback_team = create_relief_team(model=cerebras_model)
