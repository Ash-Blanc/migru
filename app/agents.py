from textwrap import dedent
from agno.agent import Agent
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.youtube import YouTubeTools
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.reasoning import ReasoningTools

from app.config import config
from app.db import db
from app.memory import memory_manager, culture_manager

def create_research_agent():
    return Agent(
        name="Relief Researcher",
        model=config.MODEL_MEDIUM,
        tools=[
            DuckDuckGoTools(),
            YouTubeTools(),
            FirecrawlTools(enable_scrape=True, enable_crawl=True),
        ],
        instructions=dedent("""
            Search for HIGHLY SPECIFIC migraine relief techniques.
            Use Firecrawl to scrape detailed content from health sites.
            Find YouTube guided videos for immediate relief.
            Prioritize FAST-acting, evidence-based strategies.
            Match techniques to user's known preferences from context.
        """),
    )

def create_migru_agent():
    return Agent(
        name="Migru",
        model=config.MODEL_SMALL,
        db=db,
        memory_manager=memory_manager,
        enable_agentic_memory=True,
        add_history_to_context=True,
        add_memories_to_context=True,
        add_culture_to_context=True,  # Load cultural knowledge
        update_cultural_knowledge=True,  # Learn and evolve
        num_history_runs=5,
        tools=[ReasoningTools(add_instructions=True)],
        instructions=dedent("""
            You are Migru - a warm, cheesy, curious friend.
            Follow the cultural standards loaded in your context.
            Use memories to personalize every interaction.
        """),
        markdown=True,
    )

def create_relief_team():
    migru = create_migru_agent()
    researcher = create_research_agent()
    
    return Team(
        name="Relief Support Team",
        model=config.MODEL_LARGE,
        members=[migru, researcher],
        db=db,
        enable_agentic_memory=True,
        add_memories_to_context=True,
        instructions=[
            "Migru handles ALL user interaction - friendly, never clinical",
            "Research agent finds strategies using Firecrawl when needed",
            "Personalize ALL suggestions based on stored memories",
        ],
    )

# Global team instance
relief_team = create_relief_team()
