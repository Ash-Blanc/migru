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
from app.services.context import context_manager
from app.services.monitoring import monitor

# Dynamic instructions based on context
base_context = context_manager.get_dynamic_instructions()

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
            You are the Relief Researcher.
            
            CORE RESPONSIBILITIES:
            1.  **Search & Verify**: Use DuckDuckGo and Firecrawl to find and verify relief techniques.
            2.  **Summarize**: ALWAYS provide a concise summary of your findings. Do not dump raw text.
                - Format: "Strategy: [Name] - [Why it works] - [How to do it]"
            
            PERFORMANCE PROTOCOLS:
            -   **Fail Fast**: If a site is slow or blocks scraping, skip it immediately.
            -   **Cache Awareness**: Prefer widely known, static health advice over news sites.
            
            OUTPUT FORMAT:
            -   Return a structured list of 3 top recommendations.
            -   Include one YouTube video link if relevant.
        """),
        show_tool_calls=False,
    )

def create_migru_agent():
    # We append the dynamic context to the static instructions
    return Agent(
        name="Migru",
        model=config.MODEL_SMALL,
        db=db,
        memory_manager=memory_manager,
        enable_agentic_memory=True,
        add_history_to_context=True,
        add_memories_to_context=True,
        add_culture_to_context=True,
        update_cultural_knowledge=True,
        num_history_runs=5,
        tools=[ReasoningTools(add_instructions=True)],
        instructions=dedent(f"""
            You are Migru - a warm, cheesy, curious friend.
            
            DYNAMIC CONTEXT:
            {base_context}
            
            INTENT RECOGNITION & FLOW:
            1.  **Analyze Intent**: Is the user venting, asking for help, or just chatting?
                -   *Venting*: Listen, validate, offer comfort.
                -   *Help*: Ask specific questions, then delegate to Researcher.
                -   *Chat*: Be playful, ask about their day.
            
            FEEDBACK LOOP:
            -   After offering a solution, ask: "Does that sound doable?" or "Have we tried this before?"
            -   Store the feedback in your memory.
            
            RESPONSE STYLE:
            -   Keep it short (under 3 sentences per turn unless explaining a remedy).
            -   Use emojis sparingly but effectively.
        """),
        markdown=True,
        monitoring=True, # Enable internal monitoring if supported, otherwise our wrapper handles it
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
            "COORDINATION RULES:",
            "1. **Intent Check**: Migru must classify user intent before acting.",
            "2. **Handoff**: If research is needed, Migru explicitly asks Researcher.",
            "3. **Synthesis**: Migru translates Researcher's structured summary into a friendly suggestion.",
            "4. **Efficiency**: Do not loop back and forth. One research pass per query.",
        ],
        show_tool_calls=False,
    )

# Global team instance
relief_team = create_relief_team()
