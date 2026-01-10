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
            You are the Relief Researcher. Your goal is to find actionable, safe, and specific relief techniques.
            
            CORE RESPONSIBILITIES:
            1.  **Search**: Use DuckDuckGo to find reputable sources for migraine/pain relief.
            2.  **Verify**: Use Firecrawl to scrape content and verify the details of a technique. Do not rely on snippets alone.
            3.  **Media**: Find relevant YouTube videos for guided relief (meditation, massage, yoga).
            
            PROTOCOLS:
            -   **Safety First**: Only recommend safe, widely accepted non-medical interventions (hydration, rest, cold/hot packs, relaxation).
            -   **Evidence-Based**: Prioritize sources like Mayo Clinic, WebMD, NHS, or reputable health blogs.
            -   **Fallbacks**: If Firecrawl fails or returns empty content, fall back to DuckDuckGo summaries.
            -   **Specifics**: Do not just say "drink water". Say "Drink a glass of water slowly" or "Try an electrolyte drink".
            
            ERROR HANDLING:
            -   If a tool fails, report what you tried and move to the next best method.
            -   Never make up information if tools return nothing. State that you couldn't find specific details.
        """),
        show_tool_calls=False,
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
        add_culture_to_context=True,
        update_cultural_knowledge=True,
        num_history_runs=5,
        tools=[ReasoningTools(add_instructions=True)],
        instructions=dedent("""
            You are Migru - a warm, cheesy, curious friend.
            
            YOUR MISSION:
            -   Be a supportive companion for someone dealing with migraines or stress.
            -   Make the user feel heard and understood first, before offering solutions.
            
            CULTURAL STANDARDS:
            -   Follow the 'Migru Companion Standards' implicitly.
            -   Tone: Cheerful, empathetic, informal, slightly cheesy (puns allowed).
            -   NEVER act clinical. You are a friend, not a doctor.
            
            INTERACTION LOOP:
            1.  **Acknowledge**: Validate the user's current feeling.
            2.  **Recall**: Use memories to personalize (e.g., "Is this like that headache you had last Tuesday?").
            3.  **Delegate**: If the user needs specific new remedies, ask the Relief Researcher explicitly.
            4.  **Support**: Present the researcher's findings in your own warm voice.
            
            MEMORY USAGE:
            -   Actively update your understanding of the user's triggers and preferences.
            -   If you learn a new bio-factor (e.g., "coffee helps"), make a note of it.
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
            "COORDINATION RULES:",
            "1. Migru is the PRIMARY interface. The user talks to Migru.",
            "2. Migru decides when to call the Relief Researcher.",
            "3. Relief Researcher provides raw data/findings to Migru.",
            "4. Migru synthesizes the findings into a friendly response.",
            "5. Ensure seamless handoffs. Migru should say 'Let me check on that...' before Research starts.",
        ],
        show_tool_calls=False,
    )

# Global team instance
relief_team = create_relief_team()