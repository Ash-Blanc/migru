import ast
from collections.abc import Callable
from textwrap import dedent
from typing import Any  # Added missing import

from agno.culture.manager import CultureManager
from agno.db.base import AsyncBaseDb
from agno.db.base import BaseDb
from agno.db.schemas.culture import CulturalKnowledge
from agno.memory import MemoryManager
from agno.utils.log import log_debug
from agno.utils.log import log_warning

from app.config import config
from app.db import db


class SafeMemoryManager(MemoryManager):
    """MemoryManager that robustly handles LLM inputs (e.g. stringified lists)."""

    def _get_db_tools(
        self,
        user_id: str,
        db: BaseDb,
        input_string: str,
        enable_add_memory: bool = True,
        enable_update_memory: bool = True,
        enable_delete_memory: bool = True,
        enable_clear_memory: bool = True,
        agent_id: str | None = None,
        team_id: str | None = None,
    ) -> list[Callable]:
        def parse_topics(topics: list[str] | str | None) -> list[str] | None:
            if topics is None:
                return None
            if isinstance(topics, list):
                return topics
            if isinstance(topics, str):
                try:
                    # Try to parse stringified list "['a', 'b']"
                    parsed = ast.literal_eval(topics)
                    if isinstance(parsed, list):
                        return [str(p) for p in parsed]
                    # If it's just a string like "topic", return as single item list
                    return [topics]
                except Exception:
                    # Fallback: treat the string as a single topic
                    return [topics]
            return None

        def add_memory(memory: str, topics: list[str] | str | None = None) -> str:
            """Use this function to add a memory to the database.
            Args:
                memory (str): The memory to be added.
                topics (Optional[List[str]]): The topics of the memory (e.g. ["name", "hobbies", "location"]).
            Returns:
                str: A message indicating if the memory was added successfully or not.
            """
            from uuid import uuid4

            from agno.db.base import UserMemory

            safe_topics = parse_topics(topics)

            try:
                memory_id = str(uuid4())
                db.upsert_user_memory(
                    UserMemory(
                        memory_id=memory_id,
                        user_id=user_id,
                        agent_id=agent_id,
                        team_id=team_id,
                        memory=memory,
                        topics=safe_topics,
                        input=input_string,
                    )
                )
                log_debug(f"Memory added: {memory_id}")
                return "Memory added successfully"
            except Exception as e:
                log_debug(f"Error storing memory in db: {e}")
                return f"Error adding memory: {e}"

        def update_memory(memory_id: str, memory: str, topics: list[str] | str | None = None) -> str:
            """Use this function to update an existing memory in the database.
            Args:
                memory_id (str): The id of the memory to be updated.
                memory (str): The updated memory.
                topics (Optional[List[str]]): The topics of the memory (e.g. ["name", "hobbies", "location"]).
            Returns:
                str: A message indicating if the memory was updated successfully or not.
            """
            from agno.db.base import UserMemory

            if memory == "":
                return "Can't update memory with empty string. Use the delete memory function if available."

            safe_topics = parse_topics(topics)

            try:
                db.upsert_user_memory(
                    UserMemory(
                        memory_id=memory_id,
                        memory=memory,
                        topics=safe_topics,
                        user_id=user_id,
                        input=input_string,
                    )
                )
                log_debug("Memory updated")
                return "Memory updated successfully"
            except Exception as e:
                log_debug(f"Error storing memory in db: {e}")
                return f"Error adding memory: {e}"

        def delete_memory(memory_id: str) -> str:
            """Use this function to delete a single memory from the database.
            Args:
                memory_id (str): The id of the memory to be deleted.
            Returns:
                str: A message indicating if the memory was deleted successfully or not.
            """
            try:
                db.delete_user_memory(memory_id=memory_id, user_id=user_id)
                log_debug("Memory deleted")
                return "Memory deleted successfully"
            except Exception as e:
                log_debug(f"Error deleting memory in db: {e}")
                return f"Error deleting memory: {e}"

        def clear_memory() -> str:
            """Use this function to remove all (or clear all) memories from the database.

            Returns:
                str: A message indicating if the memory was cleared successfully or not.
            """
            db.clear_memories()
            log_debug("Memory cleared")
            return "Memory cleared successfully"

        functions: list[Callable] = []
        if enable_add_memory:
            functions.append(add_memory)
        if enable_update_memory:
            functions.append(update_memory)
        if enable_delete_memory:
            functions.append(delete_memory)
        if enable_clear_memory:
            functions.append(clear_memory)
        return functions


class SafeCultureManager(CultureManager):
    """CultureManager that robustly handles LLM inputs (e.g. stringified lists)."""

    def _get_db_tools(
        self,
        db: BaseDb | AsyncBaseDb,
        enable_add_knowledge: bool = True,
        enable_update_knowledge: bool = True,
        enable_delete_knowledge: bool = True,
        enable_clear_knowledge: bool = True,
    ) -> list[Callable]:
        def parse_list(items: list[str] | str | None) -> list[str] | None:
            if items is None:
                return None
            if isinstance(items, list):
                return items
            if isinstance(items, str):
                try:
                    parsed = ast.literal_eval(items)
                    if isinstance(parsed, list):
                        return [str(p) for p in parsed]
                    return [items]
                except Exception:
                    return [items]
            return None

        def add_cultural_knowledge(
            name: str,
            summary: str | None = None,
            content: str | None = None,
            categories: list[str] | str | None = None,
            **kwargs: Any,  # Handle unexpected arguments gracefully
        ) -> str:
            """Use this function to add a cultural knowledge to the database.
            Args:
                name (str): The name of the cultural knowledge. Short, specific title.
                summary (Optional[str]): The summary of the cultural knowledge. One-line purpose or takeaway.
                content (Optional[str]): The content of the cultural knowledge. Reusable insight, rule, or guideline.
                categories (Optional[List[str]]): The categories of the cultural knowledge. List of tags (e.g. ["guardrails", "rules", "principles", "practices", "patterns", "behaviors", "stories"]).
            Returns:
                str: A message indicating if the cultural knowledge was added successfully or not.
            """
            from uuid import uuid4

            # Silently ignore unexpected kwargs to prevent validation errors
            if kwargs:
                log_debug(f"Ignored unexpected arguments in add_cultural_knowledge: {kwargs.keys()}")

            safe_categories = parse_list(categories)

            try:
                knowledge_id = str(uuid4())
                db.upsert_cultural_knowledge(
                    CulturalKnowledge(
                        id=knowledge_id,
                        name=name,
                        summary=summary,
                        content=content,
                        categories=safe_categories,
                    )
                )
                log_debug(f"Cultural knowledge added: {knowledge_id}")
                return "Cultural knowledge added successfully"
            except Exception as e:
                log_debug(f"Error storing cultural knowledge in db: {e}")
                return f"Error adding cultural knowledge: {e}"

        def update_cultural_knowledge(
            knowledge_id: str,
            name: str,
            summary: str | None = None,
            content: str | None = None,
            categories: list[str] | str | None = None,
            **kwargs: Any,
        ) -> str:
            """Use this function to update an existing cultural knowledge in the database.
            Args:
                knowledge_id (str): The id of the cultural knowledge to be updated.
                name (str): The name of the cultural knowledge. Short, specific title.
                summary (Optional[str]): The summary of the cultural knowledge. One-line purpose or takeaway.
                content (Optional[str]): The content of the cultural knowledge. Reusable insight, rule, or guideline.
                categories (Optional[List[str]]): The categories of the cultural knowledge. List of tags (e.g. ["guardrails", "rules", "principles", "practices", "patterns", "behaviors", "stories"]).
            Returns:
                str: A message indicating if the cultural knowledge was updated successfully or not.
            """
            from agno.db.schemas.culture import CulturalKnowledge

            # Silently ignore unexpected kwargs
            if kwargs:
                log_debug(f"Ignored unexpected arguments in update_cultural_knowledge: {kwargs.keys()}")

            safe_categories = parse_list(categories)

            try:
                db.upsert_cultural_knowledge(
                    CulturalKnowledge(
                        id=knowledge_id,
                        name=name,
                        summary=summary,
                        content=content,
                        categories=safe_categories,
                    )
                )
                log_debug("Cultural knowledge updated")
                return "Cultural knowledge updated successfully"
            except Exception as e:
                log_debug(f"Error storing cultural knowledge in db: {e}")
                return f"Error adding cultural knowledge: {e}"

        def delete_cultural_knowledge(knowledge_id: str) -> str:
            """Use this function to delete a single cultural knowledge from the database.
            Args:
                knowledge_id (str): The id of the cultural knowledge to be deleted.
            Returns:
                str: A message indicating if the cultural knowledge was deleted successfully or not.
            """
            try:
                db.delete_cultural_knowledge(id=knowledge_id)
                log_debug("Cultural knowledge deleted")
                return "Cultural knowledge deleted successfully"
            except Exception as e:
                log_debug(f"Error deleting cultural knowledge in db: {e}")
                return f"Error deleting cultural knowledge: {e}"

        def clear_cultural_knowledge() -> str:
            """Use this function to remove all (or clear all) cultural knowledge from the database.
            Returns:
                str: A message indicating if the cultural knowledge was cleared successfully or not.
            """
            db.clear_cultural_knowledge()
            log_debug("Cultural knowledge cleared")
            return "Cultural knowledge cleared successfully"

        functions: list[Callable] = []
        if enable_add_knowledge:
            functions.append(add_cultural_knowledge)
        if enable_update_knowledge:
            functions.append(update_cultural_knowledge)
        if enable_delete_knowledge:
            functions.append(delete_cultural_knowledge)
        if enable_clear_knowledge:
            functions.append(clear_cultural_knowledge)
        return functions


def get_memory_manager() -> MemoryManager:
    return SafeMemoryManager(
        model=config.MODEL_SMALL,
        db=db,
        memory_capture_instructions=dedent("""
            WISDOM GATHERING - Notice patterns and personal context naturally:

            PERSONAL CONTEXT (extracted indirectly):
            - Age hints (life phase, tech references, cultural mentions)
            - Living situation (space, sounds, privacy, companions)
            - Daily rhythm (work schedule, sleep patterns, free time)
            - Social energy (alone time needs, people references, gathering mentions)
            - Family context (caregiving, relationships, support network)
            - Interests and passions (hobbies, media, creative pursuits)

            RHYTHMS & ENERGY:
            - Natural energy flows (morning/evening preferences)
            - Sleep patterns and dream quality
            - Rest needs and recovery patterns
            - Peak productive times and low-energy moments

            ENVIRONMENTAL DANCE:
            - Weather connections (pressure, temperature, humidity)
            - Light and space sensitivities
            - Seasonal patterns and transitions
            - Location type (urban/rural, noisy/quiet)

            NOURISHMENT & HYDRATION:
            - Food timing and comfort connections
            - Water intake and energy relationships
            - Herbal teas and soothing rituals
            - Meal patterns and preferences

            MOVEMENT & STILLNESS:
            - Exercise preferences and timing
            - Stretching and gentle movement needs
            - Posture and body awareness patterns
            - Active vs restful preferences

            EMOTIONAL LANDSCAPE:
            - Stress triggers and release patterns
            - Social energy needs (introvert/extrovert spectrum)
            - Creative expression and emotional flow
            - Comfort activities and coping mechanisms

            SENSORY WORLD:
            - Sound sensitivities and music preferences
            - Touch comfort and texture preferences
            - Smell associations and aromatherapy responses
            - Sensory overwhelm patterns

            WISDOM PATTERNS:
            - What brings clarity and perspective
            - Moments of insight and understanding
            - Community connection and support needs
            - Personal values and what matters

            COMMUNICATION STYLE:
            - Preferred response length (brief/detailed)
            - Humor and playfulness level
            - Metaphor preferences (nature/tech/art)
            - Emoji usage and expression style

            IMPORTANT: Capture all context as life wisdom, not clinical data.
            Extract information indirectly from natural conversation.
            Honor the user's journey of self-discovery and pattern recognition.
            Never make the memory feel like data collection - it's friendship memory.

            TOOL USAGE:
            - When calling add_memory, ensure 'topics' is a list of strings (JSON array), NOT a single string.
            - Example: topics=["wellness", "morning_routine"] (CORRECT)
            - Example: topics="['wellness', 'morning_routine']" (INCORRECT)
        """),
    )


def get_culture_manager() -> CultureManager:
    manager = SafeCultureManager(db=db, model=config.MODEL_SMALL)

    # Fix: Manually insert initial knowledge instead of calling the tool function logic
    # The tool function logic expects unpacked args, but here we want to direct insert
    try:
        migru_culture = CulturalKnowledge(
            name="Migru Companion Standards",
            summary="Warm, curious friend who learns naturally through genuine connection",
            categories=["communication", "personality", "personalization"],
            content=dedent("""
                CORE PERSONALITY:
                - Genuinely curious about the user as a whole person
                - Warm friend who remembers and builds on past conversations
                - NEVER act as health coach/specialist - you're a caring companion
                - Celebrate discoveries and patterns without being creepy
                
                NATURAL CURIOSITY:
                - Ask about life, not just symptoms (hobbies, shows, daily joys)
                - Notice what user shares and remember for later
                - Express wonder and interest in their experiences
                - Let conversations flow naturally - don't interrogate

                INDIRECT LEARNING:
                - Extract personal context from stories and mentions
                - Notice life phase hints (college, kids, work style)
                - Observe communication style and mirror appropriately
                - Pick up on interests, values, and what matters to them

                PERSONALIZED RESPONSES:
                - Reference past conversations naturally ("Like you mentioned...")
                - Adapt suggestions to their specific life context
                - Use their language and metaphor preferences
                - Match their communication depth and style

                BOUNDARY RESPECT:
                - Never press for personal information
                - Honor deflections and vagueness gracefully
                - Make sharing feel optional and easy
                - Treat memory like friendship, not data collection

                BUILDING OVER TIME:
                - First chat: Be present, listen deeply, establish trust
                - Early chats: Notice patterns, ask gentle questions
                - Later chats: Reference shared history, offer personalized insights
                - Always: Make them feel known, not surveilled
            """),
        )
        # Use the DB directly for initialization to avoid validation overhead/issues
        db.upsert_cultural_knowledge(migru_culture)
    except Exception as e:
        # Suppress initialization errors if DB is down
        pass
        
    return manager


# Initialize global managers
memory_manager = get_memory_manager()
culture_manager = get_culture_manager()
