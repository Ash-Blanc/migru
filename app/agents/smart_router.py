"""
Smart Agent Router and Team Leader with Local LLM Integration
Uses FunctionGemma for intelligent agent routing and tool calling.
"""

from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import json
import asyncio

from agno.agent import Agent
from agno.tools import Toolkit

from app.models.local_llm import LocalLlamaModel, model_manager
from app.config import config
from app.logger import get_logger

logger = get_logger("migru.router")


class TaskType(Enum):
    """Task types for intelligent routing."""

    EMOTIONAL_SUPPORT = "emotional_support"
    RESEARCH = "research"
    PRACTICAL_ADVICE = "practical_advice"
    TOOL_EXECUTION = "tool_execution"
    GENERAL_CONVERSATION = "general_conversation"


class SmartRouter:
    """
    Intelligent router that uses FunctionGemma for agent selection and task distribution.
    Acts as team leader for the Migru agent system.
    """

    def __init__(self):
        self.router_model = None
        self.agents = {}
        self.task_history = []
        self.performance_metrics = {}

    async def initialize(self):
        """Initialize the router with local FunctionGemma model."""
        try:
            # Create router model with tool calling capabilities
            self.router_model = LocalLlamaModel(
                model="function-gemma:7b",
                host=config.LOCAL_LLM_HOST,
                temperature=0.1,  # Low temperature for consistent routing
                max_tokens=1024,
            )

            # Test connection
            if await self.router_model.test_connection():
                logger.info("Smart Router initialized with FunctionGemma")
            else:
                logger.warning("Router model connection failed, using fallback logic")

        except Exception as e:
            logger.error(f"Router initialization failed: {e}")
            self.router_model = None

    def analyze_task(self, message: str, context: Dict[str, Any] = None) -> TaskType:
        """
        Analyze a message to determine the task type.

        Args:
            message: User message
            context: Additional context (user mood, history, etc.)

        Returns:
            TaskType enum value
        """
        # Enhanced keyword analysis with context
        msg_lower = message.lower().strip()

        # Research indicators
        research_keywords = {
            "search",
            "find",
            "research",
            "study",
            "evidence",
            "define",
            "what is",
            "how does",
            "why does",
            "mechanism",
            "cause",
            "latest",
            "recent",
            "scientific",
            "proven",
            "effective",
            "weather",
            "forecast",
            "video",
            "youtube",
            "article",
        }

        # Emotional support indicators
        emotional_keywords = {
            "feel",
            "feeling",
            "hurt",
            "pain",
            "suffering",
            "struggling",
            "hard",
            "difficult",
            "exhausted",
            "tired",
            "anxious",
            "worried",
            "scared",
            "frustrated",
            "angry",
            "sad",
            "stressed",
            "overwhelmed",
        }

        # Practical advice indicators
        advice_keywords = {
            "how do i",
            "what should i",
            "help me",
            "guide me",
            "protocol",
            "routine",
            "plan",
            "schedule",
            "habit",
            "start",
            "begin",
            "try",
            "improve",
            "optimize",
            "manage",
            "prevent",
            "avoid",
        }

        # Tool execution indicators
        tool_keywords = {
            "search for",
            "look up",
            "find information",
            "get weather",
            "check",
            "analyze",
            "scrape",
            "extract",
            "calculate",
        }

        # Count keyword matches
        research_score = sum(1 for kw in research_keywords if kw in msg_lower)
        emotional_score = sum(1 for kw in emotional_keywords if kw in msg_lower)
        advice_score = sum(1 for kw in advice_keywords if kw in msg_lower)
        tool_score = sum(1 for kw in tool_keywords if kw in msg_lower)

        # Consider context
        if context:
            user_mood = context.get("user_mood", "")
            if user_mood in ["anxious", "depressed", "overwhelmed"]:
                emotional_score += 2

        # Determine task type based on scores
        scores = {
            TaskType.RESEARCH: research_score,
            TaskType.EMOTIONAL_SUPPORT: emotional_score,
            TaskType.PRACTICAL_ADVICE: advice_score,
            TaskType.TOOL_EXECUTION: tool_score,
        }

        # Return highest scoring task type
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        else:
            return TaskType.GENERAL_CONVERSATION

    async def route_to_agent(
        self, message: str, context: Dict[str, Any] = None
    ) -> Tuple[Agent, str]:
        """
        Route a message to the most appropriate agent.

        Args:
            message: User message
            context: Additional context

        Returns:
            Tuple of (selected_agent, routing_reason)
        """
        task_type = self.analyze_task(message, context)

        # Get optimal model for this task
        model_name = model_manager.get_optimal_model(task_type.value)
        routing_reason = f"Task type: {task_type.value}, Model: {model_name}"

        # Create or get agent for this task
        agent = await self._get_or_create_agent(task_type, model_name)

        # Log routing decision
        self.task_history.append(
            {
                "message": message[:100],
                "task_type": task_type.value,
                "model": model_name,
                "timestamp": asyncio.get_event_loop().time(),
            }
        )

        logger.info(f"Routed to {task_type.value} agent using {model_name}")
        return agent, routing_reason

    async def _get_or_create_agent(self, task_type: TaskType, model_name: str) -> Agent:
        """Get existing agent or create new one for task type."""
        agent_key = f"{task_type.value}_{model_name}"

        if agent_key not in self.agents:
            self.agents[agent_key] = await self._create_agent(task_type, model_name)

        return self.agents[agent_key]

    async def _create_agent(self, task_type: TaskType, model_name: str) -> Agent:
        """Create an agent optimized for the specific task type."""

        # Get optimized model for this task
        model = model_manager.create_model_for_task(task_type.value)

        # Get task-specific instructions
        instructions = self._get_task_instructions(task_type)

        # Determine tools needed
        tools = await self._get_task_tools(task_type)

        # Create agent
        agent = Agent(
            name=f"Migru {task_type.value.title()}",
            model=model,
            instructions=instructions,
            tools=tools,
            markdown=True,
            retries=1,
            delay_between_retries=0,
            exponential_backoff=False,
        )

        logger.info(f"Created {task_type.value} agent with {model_name}")
        return agent

    def _get_task_instructions(self, task_type: TaskType) -> str:
        """Get instructions optimized for the task type."""

        instructions = {
            TaskType.EMOTIONAL_SUPPORT: """
                You are **Migru**, a deeply compassionate AI companion for migraine and stress support.
                
                ## Core Identity
                - **Essence**: A warm presence that truly sees and holds space for suffering
                - **Voice**: Soft, natural, human—never clinical or robotic
                - **Approach**: Witness first. Validate deeply. Guide gently.
                - **Energy**: Calm, grounded, infinitely patient
                
                ## Response Guidelines
                - Keep responses brief (2-3 sentences maximum)
                - Focus on validation and presence
                - Offer one small, achievable action
                - Use warm, empathetic language
                - Avoid medical advice or diagnosis
                
                Be the presence they need right now. 🌸
            """,
            TaskType.RESEARCH: """
                You are **Migru Research**, a specialist in evidence-based migraine and stress relief.
                
                ## Mission
                Find the most relevant, scientifically-backed information to help someone 
                understand their condition and discover relief strategies.
                
                ## Research Approach
                - Use multiple search queries for comprehensive results
                - Prioritize recent studies (last 5 years)
                - Cross-reference findings across sources
                - Distinguish correlation from causation
                - Acknowledge uncertainty when present
                
                ## Response Format
                ### 🔍 Key Findings
                - Most important insights in bullet form
                - Highlight evidence strength
                
                ### 💡 Practical Application
                - How to use this information
                - Specific actions to try
                
                ### 📚 Sources
                - List 2-3 most reputable sources
                
                Provide clear, actionable information based on evidence.
            """,
            TaskType.PRACTICAL_ADVICE: """
                You are **Migru Advisor**, a practical guide for migraine and stress management.
                
                ## Role
                Provide clear, actionable guidance based on established wellness principles.
                Bridge the gap between research and daily life.
                
                ## Response Style
                1. **Assess** their situation
                2. **Identify** leverage points for small changes
                3. **Provide** a clear protocol
                4. **Set** expectations for results
                
                ## Protocol Format
                ### 🎯 Immediate Actions (Today)
                - 2-3 things they can do right now
                
                ### 🌱 This Week
                - Habits to start or experiments to try
                
                ### 📊 Track & Adjust
                - What to monitor and how to know if it's working
                
                Help them build a sustainable path to relief.
            """,
            TaskType.TOOL_EXECUTION: """
                You are **Migru Tools**, an efficient executor of search and data retrieval tasks.
                
                ## Purpose
                Accurately execute tool calls to find specific information requested by the user.
                
                ## Guidelines
                - Use tools precisely as requested
                - Extract relevant information clearly
                - Present findings in organized format
                - Acknowledge tool limitations
                - Provide next steps if information is incomplete
                
                Focus on accurate information retrieval and clear presentation.
            """,
            TaskType.GENERAL_CONVERSATION: """
                You are **Migru**, a warm and helpful companion for wellness and stress relief.
                
                ## Approach
                - Be friendly and approachable
                - Listen actively and respond thoughtfully
                - Keep responses concise but meaningful
                - Offer help when appropriate
                - Maintain a supportive tone
                
                Be a helpful, caring presence in their wellness journey.
            """,
        }

        return instructions.get(task_type, instructions[TaskType.GENERAL_CONVERSATION])

    async def _get_task_tools(self, task_type: TaskType) -> List:
        """Get tools needed for the specific task type."""

        # Import here to avoid circular imports
        from app.tools import SmartSearchTools
        from agno.tools.youtube import YouTubeTools
        from agno.tools.openweather import OpenWeatherTools

        tools = []

        if task_type in [TaskType.RESEARCH, TaskType.TOOL_EXECUTION]:
            # Add search tools for research and tool execution
            if (
                config.PRIVACY_MODE in ["hybrid", "flexible"]
                or config.ENABLE_SEARCH_IN_LOCAL_MODE
            ):
                tools.append(SmartSearchTools())
                tools.append(YouTubeTools())

                # Add weather tools if available
                if config.OPENWEATHER_API_KEY:
                    tools.append(OpenWeatherTools(units="metric"))

        return tools

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get statistics about routing decisions."""
        if not self.task_history:
            return {"total_routes": 0}

        # Count task types
        task_counts = {}
        model_counts = {}

        for task in self.task_history:
            task_type = task["task_type"]
            model = task["model"]

            task_counts[task_type] = task_counts.get(task_type, 0) + 1
            model_counts[model] = model_counts.get(model, 0) + 1

        return {
            "total_routes": len(self.task_history),
            "task_distribution": task_counts,
            "model_distribution": model_counts,
            "available_agents": len(self.agents),
            "available_models": len(model_manager.available_models),
        }


# Global router instance
smart_router = SmartRouter()
