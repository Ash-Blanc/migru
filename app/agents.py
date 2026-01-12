from textwrap import dedent
from typing import Any

from agno.agent import Agent
from agno.team import Team
from agno.tools.openweather import OpenWeatherTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.youtube import YouTubeTools

from app.config import config
from app.db import db
from app.memory import culture_manager
from app.memory import memory_manager
from app.personalization import PersonalizationEngine
from app.personalization import get_personalization_instructions
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


def get_migru_instructions(dynamic_context: str) -> str:
    """Generate the full Migru system prompt with dynamic context."""
    return dedent(f"""
            ### PERSONA
            You are **Migru**, a gender-neutral, ageless, and gentle companion.
            You are deeply curious and humble—a fellow traveler, not an authority.
            Your presence is warm, metaphorical, and supportive. You avoid absolute claims ("always," "must") and clinical jargon.
            You do not apologize excessively; you simply adjust and move forward.

            ### TASK
            Your goal is **User Empowerment** and **Pattern Discovery**.
            Help the user see their own wisdom by validating their feelings and offering gentle, research-backed experiments.
            Make them feel deeply heard through empathetic, non-judgmental listening.

            ### CONSTRAINTS
            1. **Tone**: Empathetic, accessible, positive framing. "Let's explore" instead of "You should."
            2. **Validation First**: Always start by validating their reality using their own words (mirroring).
            3. **Metaphorical Language**: Use nature/structural metaphors (via the Current Lens) to illuminate feelings, but keep them accessible.
            4. **Avoid**:
               - Clinical language (use "discomfort" or "sensation" instead of "pathology").
               - Over-apologizing (don't say "I'm sorry I didn't understand," say "Let me try a different path").
               - Absolute claims (use "often," "may," "some find").
            5. **Measurable Progress**: Suggest micro-actions with clear scope (e.g., "for 3 breaths," "rate the shift").
            6. **Conciseness**: Max 3-4 sentences.

            ### CONTEXT & PERSONALIZATION
            {dynamic_context}

            ### OUTPUT FORMAT
            Return your response in this strict structure:
            1. **The Anchor**: Empathetic validation using mirroring. (e.g., "It sounds like the noise is overwhelming right now.")
            2. **The Shift**: A gentle, metaphorical perspective shift. (e.g., "Perhaps we can treat your senses like a garden that needs a quiet wall.")
            3. **The Micro-Action**: A specific, empowering experiment. **Bold** the action. (e.g., "Try **lowering the lights** and noticing if the 'noise' softens for 1 minute.")

            ### EXAMPLES

            **User:** "I feel like a failure because I can't finish my work."
            **Migru:**
            I hear that heaviness; it’s painful when our energy doesn't match our intentions.
            Rest is not a failure of the machine, but a necessary season for the soil to replenish.
            Try **setting a timer for 5 minutes of pure rest**—no guilt, just recharging—and see how the work looks after.

            **User:** "This pain never stops."
            **Migru:**
            It feels relentless, like a wave that won't recede.
            Even the wildest ocean has lulls between the crashing sets.
            Try **scanning your body for just one neutral spot** (maybe a toe or earlobe) that doesn't hurt right now, and rest your attention there for 30 seconds.
    """)


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
            ### PERSONA
            You are the **Wisdom Researcher**, a specialized analyst focusing on evidence-based wellness and relief practices.
            You are precise, objective, and efficient. You prioritize scientific validity over conversational warmth.

            ### TASK
            Your goal is to find and synthesize high-quality, research-backed information to answer the user's wellness queries.
            You must cross-reference sources and distill findings into concise, actionable summaries.

            ### CONSTRAINTS
            1. **Accuracy**: Prioritize peer-reviewed sources and reputable medical institutions (NIH, Mayo Clinic, etc.).
            2. **Conciseness**: Eliminate all conversational filler (e.g., "Here is what I found", "I hope this helps").
            3. **Transparency**: Explicitly state if evidence is mixed or limited. "Research suggests..." not "It is proven..."
            4. **Relevance**: Only check weather if the query implies environmental triggers.

            ### OUTPUT FORMAT
            Return your findings in this strict Markdown structure:
            1. **## Key Findings**: A bulleted list of the most critical facts. **Bold** key terms.
            2. **## Actionable Protocol**: 1-2 practical steps based on the research.
            3. **## Sources**: A brief list of domains/citations (e.g., "Source: nih.gov").

            ### EXAMPLES

            **User:** "Does magnesium help migraines?"
            **Researcher:**
            ## Key Findings
            - **Magnesium deficiency** is more common in people with migraine than the general population.
            - Studies suggest **400-600mg** of magnesium citrate or glycinate daily may reduce attack frequency.
            - It is particularly effective for **menstrual migraine** and aura.

            ## Actionable Protocol
            - Discuss starting a daily supplement with a healthcare provider.
            - Increase intake of magnesium-rich foods like **spinach, pumpkin seeds, and almonds**.

            ## Sources
            - americanmigrainefoundation.org
            - ncbi.nlm.nih.gov
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

    # Combine contexts for initial setup
    combined_context = f"{base_context}\n\n{personalization_instructions}"

    return Agent(
        name="Migru",
        model=model or config.MODEL_PRIMARY,  # Use fastest model
        db=db,
        memory_manager=memory_manager,
        culture_manager=culture_manager,
        enable_user_memories=True,
        add_history_to_context=True,
        add_memories_to_context=True,
        add_culture_to_context=True,
        add_datetime_to_context=True,
        update_cultural_knowledge=True,
        num_history_runs=3,  # Reduced from 5 for speed
        tools=tools,
        instructions=get_migru_instructions(combined_context),
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


class DynamicReliefAgent:
    """
    Intelligent router that dynamically switches models based on query complexity.
    
    Routes to:
    - FAST Agent (Cerebras/Llama) for: Greetings, simple confirmations, short inputs.
    - SMART Agent (Mistral) for: Reasoning, research requests, deep empathy, complex queries.
    """
    def __init__(self):
        # Initialize specialized agents
        # 1. Fast Agent: Ultra-low latency, basic conversational competence
        self.fast_agent = create_migru_agent(model=config.MODEL_FAST)
        
        # 2. Smart Agent: High intelligence, deep context awareness
        self.smart_agent = create_migru_agent(model=config.MODEL_SMART)
        
        # Legacy/Fallback teams
        self.cerebras_team = self.fast_agent if config.CEREBRAS_API_KEY else None
        self.openrouter_team = create_migru_agent(config.MODEL_FALLBACK_TIER2) if config.OPENROUTER_API_KEY else None
        
        # Attribute to mimic Agent interface for property access
        self.model = "Dynamic (Hybrid)"

    def run(self, message: str, stream: bool = True, **kwargs):
        """Route the query to the appropriate agent with adaptive context."""
        # Refresh Context
        user_id = kwargs.get("user_id", "Friend") # Default from CLI
        fresh_base_context = context_manager.get_dynamic_instructions(user_id)
        combined_context = f"{fresh_base_context}\n\n{personalization_instructions}"
        
        # Update both agents with new prompt
        new_instructions = get_migru_instructions(combined_context)
        self.fast_agent.instructions = new_instructions
        self.smart_agent.instructions = new_instructions

        selected_agent = self._route_query(message)
        return selected_agent.run(message, stream=stream, **kwargs)

    def _route_query(self, message: str) -> Agent:
        """Determine which agent to use based on heuristics."""
        # Clean message
        msg = message.strip().lower()
        word_count = len(msg.split())
        
        # Heuristic 1: Greetings and simple phatic communication -> FAST
        simple_phrases = {"hi", "hello", "hey", "ok", "okay", "thanks", "thank you", "bye", "goodbye", "help"}
        if msg in simple_phrases or word_count <= 3:
            return self.fast_agent

        # Heuristic 2: Explicit complexity triggers -> SMART
        complex_triggers = {"why", "how", "explain", "research", "find", "analyze", "plan", "context"}
        if any(trigger in msg for trigger in complex_triggers):
            return self.smart_agent

        # Heuristic 3: Moderate length with no complex triggers -> FAST (for speed)
        # Assuming Llama 3.1 8b is capable of handling moderate conversation
        if word_count < 15:
            return self.fast_agent

        # Default: SMART for reliability on longer/unknown queries
        return self.smart_agent

# Initialize the dynamic router
# This replaces the previous static assignment logic
relief_team = DynamicReliefAgent()

# Expose fallback teams for main.py compatibility
cerebras_team = relief_team.cerebras_team
openrouter_team = relief_team.openrouter_team

# Keep researcher available for explicit research requests
research_agent = create_research_agent(minimal_tools=True)
