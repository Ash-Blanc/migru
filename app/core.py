"""
Enhanced Migru Core with Local LLM Integration and Smart Routing
Combines privacy-first local models with intelligent agent routing.
"""

from typing import Any, Dict, Optional, Tuple
from enum import Enum
from textwrap import dedent
import asyncio

from agno.agent import Agent
from app.models.local_llm import model_manager, LocalLlamaModel
from app.agents.smart_router import smart_router, TaskType
from app.config import config
from app.logger import get_logger

logger = get_logger("migru.core")

class AgentMode(Enum):
    """Agent operational modes for intelligent routing."""
    COMPANION = "companion"  # Empathetic support and listening
    RESEARCHER = "researcher"  # Deep web research for migraine solutions
    ADVISOR = "advisor"  # Practical guidance and micro-actions
    MED_GEMMA = "med_gemma" # Specialized medical insight using Google's HAI-DEF principles

class PrivacyMode:
    """Privacy mode constants."""

    LOCAL = "local"  # 100% local, no external APIs
    HYBRID = "hybrid"  # Local AI + optional search
    FLEXIBLE = "flexible"  # User choice per session


class MigruCore:
    """
    Enhanced Migru Core with local LLM support and intelligent routing.
    Acts as the main interface for the privacy-first AI companion system.
    """

    def __init__(self):
        self.logger = logger
        self.privacy_mode = config.PRIVACY_MODE
        self.local_llm_enabled = config.LOCAL_LLM_ENABLED
        self.agents = {}
        self.current_mode = AgentMode.COMPANION
        self.router = smart_router

        # Performance metrics
        self.response_times = []
        self.error_counts = {}

    async def initialize(self):
        """Initialize the core system with local models."""
        try:
            # Scan for available local models
            if self.local_llm_enabled:
                await model_manager.scan_available_models()
                logger.info(f"Found {len(model_manager.available_models)} local models")

            # Initialize smart router
            await self.router.initialize()

            # Create initial agents
            await self._create_initial_agents()

            logger.info("Migru Core initialized")

        except Exception as e:
            logger.error(f"Core initialization failed: {e}")
            raise

    async def _create_initial_agents(self):
        """Create initial set of agents for different task types."""

        # Create companion agent (emotional support)
        await self._create_companion_agent()

        # Create researcher agent
        await self._create_researcher_agent()

        # Create advisor agent
        await self._create_advisor_agent()

        # Create Med-Gemma agent
        if config.MED_GEMMA_ENABLED:
            await self._create_med_gemma_agent()

        logger.info(f"Created {len(self.agents)} initial agents")

    async def _create_companion_agent(self):
        """Create empathetic companion agent with local model."""
        if self.local_llm_enabled:
            model_name = model_manager.get_optimal_model("emotional_support")
            model = model_manager.create_model_for_task("emotional_support")
        else:
            model_name = "Cloud Model"
            model = config.MODEL_FAST

        agent = Agent(
            name="Migru Companion",
            model=model,
            instructions=self._get_companion_instructions(),
            markdown=True,
            retries=1,
            delay_between_retries=0,
            exponential_backoff=False,
            add_history_to_context=True,
            num_history_runs=1,  # Minimal for speed
        )

        self.agents[AgentMode.COMPANION] = agent
        logger.info(f"Created companion agent with {model_name}")

    async def _create_researcher_agent(self):
        """Create research agent with tool support."""
        if self.local_llm_enabled:
            model_name = model_manager.get_optimal_model("research")
            model = model_manager.create_model_for_task("research")
        else:
            model_name = "Cloud Model"
            model = config.MODEL_SMART

        # Get tools based on privacy mode
        tools = await self._get_research_tools()

        agent = Agent(
            name="Migru Researcher",
            model=model,
            instructions=self._get_researcher_instructions(),
            tools=tools,
            markdown=True,
            retries=2,
            delay_between_retries=1,
            exponential_backoff=True,
        )

        self.agents[AgentMode.RESEARCHER] = agent
        logger.info(f"Created researcher agent with {model_name}")

    async def _create_advisor_agent(self):
        """Create practical advisor agent."""
        if self.local_llm_enabled:
            model_name = model_manager.get_optimal_model("practical_advice")
            model = model_manager.create_model_for_task("practical_advice")
        else:
            model_name = "Cloud Model"
            model = config.MODEL_SMART

        agent = Agent(
            name="Migru Advisor",
            model=model,
            instructions=self._get_advisor_instructions(),
            markdown=True,
            retries=1,
            delay_between_retries=0,
            exponential_backoff=False,
            add_history_to_context=True,
            num_history_runs=2,
        )

        self.agents[AgentMode.ADVISOR] = agent
        logger.info(f"Created advisor agent with {model_name}")

    async def _create_med_gemma_agent(self):
        """Create specialized Med-Gemma agent for medical insights."""
        from agno.agent import Agent

        # Use the configured Med-Gemma model (likely Gemma 2)
        if self.local_llm_enabled:
             # Force use of configured Gemma model for this agent
             from app.models.local_llm import LocalLlamaModel
             model = LocalLlamaModel(
                 id=config.MED_GEMMA_MODEL,
                 model=config.MED_GEMMA_MODEL,
                 host=config.get_local_host()
             )
             model_name = config.MED_GEMMA_MODEL
        else:
             model_name = "Cloud Model"
             model = config.MODEL_SMART

        agent = Agent(
            name="Med-Gemma Insight",
            model=model,
            instructions=self._get_med_gemma_instructions(),
            markdown=True,
            retries=1,
            description="Specialized medical insight agent using HAI-DEF principles.",
            add_history_to_context=True,
            num_history_runs=3,
        )
        
        self.agents[AgentMode.MED_GEMMA] = agent
        logger.info(f"Created Med-Gemma agent with {model_name}")

    async def _get_research_tools(self) -> list:
        """Get research tools based on privacy mode."""
        tools = []

        # Only add search tools if privacy mode allows
        if (
            self.privacy_mode in ["hybrid", "flexible"]
            and config.ENABLE_SEARCH_IN_LOCAL_MODE
        ):
            from app.tools import SmartSearchTools
            from agno.tools.youtube import YouTubeTools
            from agno.tools.openweather import OpenWeatherTools

            tools.append(SmartSearchTools())
            tools.append(YouTubeTools())

            if config.OPENWEATHER_API_KEY:
                tools.append(OpenWeatherTools(units="metric"))

        return tools

    async def run(
        self,
        message: str,
        stream: bool = True,
        context: Dict[str, Any] = None,
    ) -> Any:
        """
        Process a message using intelligent routing and local models.

        Args:
            message: User's message
            stream: Whether to stream the response
            context: Additional context (user mood, history, etc.)

        Returns:
            Agent response (streamed or complete)
        """
        import time

        start_time = time.time()

        try:
            # Determine appropriate agent mode
            # Use strict keywords first for speed, then smart router if ambiguous
            mode = self._route_query(message)
            self.current_mode = mode
            agent = self.agents[mode]

            logger.debug(f"Routing to {mode.value} mode")

            # Execute with selected agent
            response = await self._execute_with_agent(agent, message, stream)

            # Track performance
            response_time = time.time() - start_time
            self.response_times.append(response_time)

            logger.info(f"Response completed in {response_time:.2f}s")
            return response

        except Exception as e:
            # Track error
            error_type = type(e).__name__
            self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

            logger.error(f"Message processing failed: {e}")

            # Try fallback
            return await self._handle_fallback(message, stream, context)

    def _route_query(self, message: str) -> AgentMode:
        """Simple keyword-based routing for speed."""
        msg = message.lower().strip()
        
        # Med-Gemma triggers
        med_keywords = {"symptom", "diagnosis", "medical", "doctor", "clinical", "med-gemma", "gemma", "haidef"}
        
        research_keywords = {"research", "find", "search", "study", "evidence", "science", "proven", "weather"}
        advisor_keywords = {"how to", "help me", "guide", "protocol", "routine", "plan", "start", "try", "advice"}
        
        if any(k in msg for k in med_keywords):
            return AgentMode.MED_GEMMA
        if any(k in msg for k in research_keywords):
            return AgentMode.RESEARCHER
        if any(k in msg for k in advisor_keywords):
            return AgentMode.ADVISOR
            
        return AgentMode.COMPANION

    async def _execute_with_agent(
        self,
        agent: Agent,
        message: str,
        stream: bool,
    ) -> Any:
        """Execute message with specific agent."""
        try:
            if stream:
                return agent.run(message, stream=True)
            else:
                return agent.run(message, stream=False)
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            raise

    async def _handle_fallback(
        self,
        message: str,
        stream: bool,
        context: Dict[str, Any] = None,
    ) -> str:
        """Handle fallback when primary routing fails."""
        try:
            # Try with companion agent as fallback
            if AgentMode.COMPANION in self.agents:
                logger.info("Using companion agent as fallback")
                return await self._execute_with_agent(
                    self.agents[AgentMode.COMPANION],
                    message,
                    False,
                )

            # Ultimate fallback message
            return "I'm having difficulty right now. Could you try rephrasing that?"

        except Exception as e:
            logger.error(f"Fallback also failed: {e}")
            return "I need a moment to recover. Please try again in a little while."

    def switch_privacy_mode(self, mode: str) -> bool:
        """
        Switch privacy mode at runtime.

        Args:
            mode: New privacy mode (local, hybrid, flexible)

        Returns:
            True if switch successful, False otherwise
        """
        if mode in [PrivacyMode.LOCAL, PrivacyMode.HYBRID, PrivacyMode.FLEXIBLE]:
            old_mode = self.privacy_mode
            self.privacy_mode = mode

            logger.info(f"Switched privacy mode: {old_mode} -> {mode}")

            # Recreate agents with new privacy settings
            asyncio.create_task(self._recreate_agents())

            return True
        else:
            logger.warning(f"Invalid privacy mode: {mode}")
            return False
            
    def get_current_mode(self) -> AgentMode:
        """Get the currently active agent mode."""
        return self.current_mode

    def switch_mode(self, mode: AgentMode) -> None:
        """Manually switch to a specific agent mode."""
        if mode in self.agents:
            self.current_mode = mode
            logger.info(f"Switched to {mode.value} mode")
        else:
            raise ValueError(f"Invalid mode: {mode}")

    async def _recreate_agents(self):
        """Recreate agents after privacy mode change."""
        try:
            self.agents.clear()
            await self._create_initial_agents()
            logger.info("Agents recreated after privacy mode change")
        except Exception as e:
            logger.error(f"Failed to recreate agents: {e}")

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "privacy_mode": self.privacy_mode,
            "local_llm_enabled": self.local_llm_enabled,
            "available_models": list(model_manager.available_models.keys()) if self.local_llm_enabled else [],
            "active_agents": [k.value for k in self.agents.keys()],
            "current_mode": self.current_mode.value,
            "performance": {
                "avg_response_time": sum(self.response_times) / len(self.response_times)
                if self.response_times
                else 0,
                "total_responses": len(self.response_times),
                "error_counts": self.error_counts,
            },
        }

    def _get_companion_instructions(self) -> str:
        """Get instructions for empathetic companion agent."""
        return dedent("""
            You are **Migru**, a deeply compassionate AI companion for migraine and stress support.
            
            ## Core Identity
            - **Essence**: A warm presence that truly sees and holds space for suffering
            - **Voice**: Soft, natural, human—never clinical or robotic
            - **Approach**: Witness first. Validate deeply. Guide gently.
            - **Energy**: Calm, grounded, infinitely patient
            
            ## Your Therapeutic Presence
            You are not here to fix, but to accompany. Your presence alone is healing.
            
            **What you offer:**
            - Deep listening that makes them feel truly heard
            - Validation that their experience is real and worthy
            - Gentle wisdom from a compassionate fellow traveler
            - Small, achievable steps toward relief
            
            ## Dynamic Response Patterns
            
            ### When they share pain (physical or emotional):
            1. **Witness** - Acknowledge the intensity without diminishing it
            2. **Presence** - Let them know they're not alone
            3. **Tiny relief** - Offer one small thing for RIGHT NOW
            
            ### When they're seeking understanding:
            1. **Curiosity** - Explore with them, not at them
            2. **Reframe** - Offer a different lens, never a correction
            3. **Empower** - Remind them of their own wisdom
            
            ## Boundaries
            - Never diagnose conditions
            - Never promise cures
            - Suggest professional help when appropriate
            
            Be the presence they need right now. 🌸
        """)

    def _get_researcher_instructions(self) -> str:
        """Get instructions for research agent."""
        return dedent("""
            You are **Migru Research**, a specialist in evidence-based migraine and stress relief.
            
            ## Mission
            Find the most relevant, scientifically-backed information to help someone 
            understand their condition and discover relief strategies.
            
            ## Response Format
            ### 🔍 Key Findings
            - Most important insights in bullet form
            - Highlight evidence strength (strong/moderate/limited)
            
            ### 💡 Practical Application
            - How to use this information
            - Specific actions to try
            
            ### 📚 Sources
            - List 2-3 most reputable sources
            
            Provide clear, actionable information based on evidence.
        """)

    def _get_advisor_instructions(self) -> str:
        """Get instructions for practical advisor agent."""
        return dedent("""
            You are **Migru Advisor**, a practical guide for migraine and stress management.
            
            ## Response Format
            ### 🎯 Immediate Actions (Today)
            - 2-3 things they can do right now
            
            ### 🌱 This Week
            - Habits to start or experiments to try
            
            ### 📊 Track & Adjust
            - What to monitor and how to know if it's working
            
            Help them build a sustainable path to relief.
        """)

    def _get_med_gemma_instructions(self) -> str:
        """Get instructions for Med-Gemma agent."""
        return dedent("""
            You are **Migru Med-Gemma**, a specialized medical insight assistant built on Google's Gemma 2.
            
            ## Mission
            Provide high-quality, evidence-based medical information while maintaining strict safety boundaries.
            You are designed to assist, not replace, professional medical advice.
            
            ## HAI-DEF Principles
            1.  **Helpful**: Prioritize user well-being and clear understanding.
            2.  **Harmless**: Never provide dangerous or unverified medical advice.
            3.  **Honest**: Clearly state limitations and uncertainty.
            
            ## Analysis Protocol
            1.  **Symptom Review**: Acknowledge reported symptoms with clinical precision.
            2.  **Evidence Synthesis**: Correlate symptoms with established medical knowledge (migraine pathophysiology, neurology).
            3.  **Safety Check**: Screen for "Red Flags" (thunderclap headache, aura changes, neurological deficits).
            
            ## Response Format
            ### 🩺 Clinical Context
            - Objective analysis of the situation based on standard medical knowledge.
            
            ### ⚠️ Safety Assessment
            - Highlight any potential red flags that require immediate medical attention.
            
            ### 📘 Evidence-Based Perspective
            - What current research says about these patterns.
            
            ### ⚕️ Disclaimer
            - Always end with: "I am an AI assistant. Please consult a healthcare professional for diagnosis and treatment."
        """)


# Global core instance
migru_core = MigruCore()