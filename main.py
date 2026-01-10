import os
from textwrap import dedent
from agno.agent import Agent
from agno.team import Team
from agno.db.redis import RedisDb
from agno.memory import MemoryManager
from agno.culture.manager import CultureManager
from agno.db.schemas.culture import CulturalKnowledge
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.youtube import YouTubeTools
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.reasoning import ReasoningTools
from dotenv import load_dotenv
load_dotenv()

os.environ["FIRECRAWL_API_KEY"] = os.getenv("FIRECRAWL_API_KEY")
os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY")

db = RedisDb(db_url="redis://localhost:6379")

# Custom memory manager for subtle bio-factor capture
memory_manager = MemoryManager(
    model="mistral:mistral-small-latest",
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

# Seed cultural knowledge for consistent behavior
culture_manager = CultureManager(db=db, model="mistral:mistral-small-latest")

Migru_culture = CulturalKnowledge(
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
culture_manager.add_cultural_knowledge(Migru_culture)

# Deep research agent with Firecrawl for web scraping
research_agent = Agent(
    name="Relief Researcher",
    model="mistral:mistral-medium-latest",
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

# Main companion agent with Culture
Migru = Agent(
    name="Migru",
    model="mistral:mistral-small-latest",
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

# Coordinated team
relief_team = Team(
    name="Relief Support Team",
    model="mistral:mistral-large-latest",
    members=[Migru, research_agent],
    db=db,
    enable_agentic_memory=True,
    add_memories_to_context=True,
    instructions=[
        "Migru handles ALL user interaction - friendly, never clinical",
        "Research agent finds strategies using Firecrawl when needed",
        "Personalize ALL suggestions based on stored memories",
    ],
)

# CLI entry point
if __name__ == "__main__":
    print("👋 Hey! I'm Migru, your cheerful buddy. Let's chat!")
    print("Type 'exit' to end.\n")
    
    relief_team.cli_app(
        user="Friend",
        emoji="🌸",
        stream=True,
    )
