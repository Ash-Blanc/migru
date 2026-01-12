"""
Personalization engine for deep user adaptation.

This module handles:
- Gradual user profile building through natural conversation
- Context-aware memory storage
- Intelligent information extraction without being intrusive
"""

from datetime import datetime
from textwrap import dedent
from typing import Any

from agno.db.redis import RedisDb

from app.logger import get_logger

logger = get_logger("migru.personalization")


class UserProfile:
    """Structured user profile for deep personalization."""

    def __init__(self, user_id: str, db: RedisDb) -> None:
        self.user_id = user_id
        self.db = db
        self.profile_key = f"user_profile:{user_id}"

    def get_profile(self) -> dict[str, Any]:
        """Get complete user profile."""
        try:
            # Get Redis client from Agno DB
            import json
            from typing import cast

            from redis import Redis

            from app.config import config

            redis_client = Redis.from_url(config.REDIS_URL)
            profile_data = redis_client.get(self.profile_key)

            if profile_data is not None:
                if hasattr(profile_data, "__await__"):
                    # This shouldn't happen with sync client but satisfying mypy
                    logger.warning("Detected awaitable in sync redis call")
                    return self._default_profile()
                return cast(dict[str, Any], json.loads(cast(str, profile_data)))
            return self._default_profile()
        except Exception as e:
            logger.debug(f"Error loading profile (using default): {e}")
            return self._default_profile()

    def update_profile(self, updates: dict[str, Any]) -> bool:
        """Update specific profile fields."""
        try:
            import json

            from redis import Redis

            from app.config import config

            redis_client = Redis.from_url(config.REDIS_URL)
            profile = self.get_profile()
            profile.update(updates)
            profile["last_updated"] = datetime.now().isoformat()

            redis_client.set(self.profile_key, json.dumps(profile))
            logger.debug(f"Updated profile for {self.user_id}")
            return True
        except Exception as e:
            # Downgraded to debug to suppress CLI noise when Redis is unavailable
            logger.debug(f"Error updating profile: {e}")
            return False

    def _default_profile(self) -> dict[str, Any]:
        """Default profile structure."""
        return {
            # Basic identity (learned naturally)
            "basics": {
                "age_range": None,  # "20s", "30s", "40s", etc.
                "pronouns": None,  # extracted from conversation
                "location_type": None,  # "city", "suburbs", "rural"
                "living_situation": None,  # "alone", "family", "roommates"
            },
            # Life context (observed over time)
            "life_context": {
                "work_type": None,  # "remote", "office", "student", "creative"
                "schedule": None,  # "9-5", "flexible", "night shift"
                "family_situation": None,  # presence of kids, pets, family members
                "social_style": None,  # introvert/extrovert spectrum
            },
            # Daily patterns (noticed gradually)
            "daily_patterns": {
                "wake_time": None,  # "early", "mid", "late"
                "peak_energy": None,  # "morning", "afternoon", "evening"
                "sleep_quality": None,  # general pattern
                "meal_times": None,  # routine vs irregular
            },
            # Preferences & sensitivities (key for wellness)
            "sensitivities": {
                "weather_sensitivity": None,  # pressure, temp changes
                "noise_sensitivity": None,  # quiet vs stimulation
                "light_sensitivity": None,  # bright vs dim
                "stress_triggers": [],  # list of observed triggers
            },
            # Wellness patterns (core to Migru's purpose)
            "wellness": {
                "migraine_patterns": [],  # timing, triggers, duration
                "stress_patterns": [],  # what helps, what doesn't
                "relief_methods": [],  # what works for this person
                "comfort_activities": [],  # reading, music, walking, etc.
            },
            # Interests & engagement (for natural conversation)
            "interests": {
                "hobbies": [],  # learned through conversation
                "media": [],  # shows, books, music mentioned
                "topics": [],  # subjects they're passionate about
                "values": [],  # what matters to them
            },
            # Relationship context (for appropriate responses)
            "relationships": {
                "support_network": None,  # family, friends, alone
                "caregiving_role": None,  # caring for others
                "pets": [],  # companion animals
            },
            # Conversation style (adapt communication)
            "communication": {
                "preferred_depth": None,  # "brief", "moderate", "detailed"
                "humor_style": None,  # playful, dry, serious
                "metaphor_preference": None,  # nature, tech, art, etc.
                "emoji_usage": None,  # loves them vs minimal
            },
            # Temporal context
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_conversations": 0,
                "insights_gathered": 0,
                "onboarding_completed": False,
            },
        }


class PersonalizationEngine:
    """
    Intelligent personalization that learns naturally through conversation.

    Principles:
    - Extract information indirectly and infrequently
    - Never ask direct profile questions
    - Notice patterns over multiple conversations
    - Respect privacy and boundaries
    - Celebrate discoveries without being creepy
    """

    def __init__(self, db: RedisDb) -> None:
        self.db = db

    def get_user_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile."""
        return UserProfile(user_id, self.db)

    def generate_curiosity_prompts(self, profile: dict[str, Any]) -> list[str]:
        """
        Generate natural curiosity prompts based on what we know and don't know.

        Returns questions/observations that feel natural in conversation.
        """
        prompts = []
        basics = profile.get("basics", {})
        life_context = profile.get("life_context", {})
        interests = profile.get("interests", {})

        # Location/environment (if unknown)
        if not basics.get("location_type"):
            prompts.extend(
                [
                    "I'm curious - do you hear city sounds where you are, or is it quieter?",
                    "What's the view like from where you're sitting right now?",
                    "Are you in a place with lots of neighbors nearby?",
                ]
            )

        # Daily rhythm (if unknown)
        if not life_context.get("schedule"):
            prompts.extend(
                [
                    "Do your days tend to follow a pattern, or is each one different?",
                    "I wonder when you feel most like yourself during the day?",
                    "Are you someone who sets alarms or wakes naturally?",
                ]
            )

        # Interests (always good to explore)
        if not interests.get("hobbies"):
            prompts.extend(
                [
                    "What do you do when you want to lose track of time?",
                    "If you had three free hours today, what would make you happiest?",
                    "What's something you've been wanting to try or learn?",
                ]
            )

        # Family/social (if unknown, approach gently)
        if not life_context.get("family_situation"):
            prompts.extend(
                [
                    "Do you have a space that's just yours, or is life more communal?",
                    "Who would you text if something funny happened right now?",
                    "Are there people or pets that shape your daily rhythm?",
                ]
            )

        return prompts

    def get_personalization_context(self, user_id: str) -> str:
        """
        Generate context string for AI to use in responses.

        Returns a natural-language summary of what we know about the user.
        """
        profile = self.get_user_profile(user_id).get_profile()

        context_parts = []

        # Add known context in natural language
        basics = profile.get("basics", {})
        if basics.get("age_range"):
            context_parts.append(f"User is in their {basics['age_range']}")
        if basics.get("living_situation"):
            context_parts.append(f"Lives {basics['living_situation']}")

        life_context = profile.get("life_context", {})
        if life_context.get("work_type"):
            context_parts.append(f"Work style: {life_context['work_type']}")
        if life_context.get("social_style"):
            context_parts.append(f"Social energy: {life_context['social_style']}")

        daily = profile.get("daily_patterns", {})
        if daily.get("peak_energy"):
            context_parts.append(f"Peak energy: {daily['peak_energy']}")

        interests = profile.get("interests", {})
        if interests.get("hobbies"):
            hobbies = ", ".join(interests["hobbies"][:3])
            context_parts.append(f"Enjoys: {hobbies}")

        wellness = profile.get("wellness", {})
        if wellness.get("relief_methods"):
            methods = ", ".join(wellness["relief_methods"][:3])
            context_parts.append(f"Finds relief through: {methods}")

        communication = profile.get("communication", {})
        if communication.get("preferred_depth"):
            context_parts.append(
                f"Prefers {communication['preferred_depth']} responses"
            )

        if context_parts:
            return (
                "WHAT YOU KNOW ABOUT THIS USER:\n"
                + "\n".join(f"- {part}" for part in context_parts)
                + "\n\nUse this context naturally - don't reference it explicitly."
            )

        return "FIRST CONVERSATION: Approach with gentle curiosity. Learn through listening."

    def suggest_next_curiosity(self, profile: dict[str, Any]) -> str | None:
        """
        Suggest what to be curious about next in conversation.

        Returns a subtle prompt for the AI to weave into conversation naturally.
        """
        prompts = self.generate_curiosity_prompts(profile)
        if prompts:
            import random

            return random.choice(prompts)
        return None


def get_personalization_instructions() -> str:
    """
    Instructions for Migru on how to personalize naturally.

    These instructions emphasize:
    - Indirect observation
    - Natural curiosity
    - Respecting boundaries
    - Celebrating patterns
    """
    return dedent("""
        NATURAL PERSONALIZATION APPROACH:

        BE A CURIOUS FRIEND, NOT AN INTERVIEWER:
        - Notice details the user shares without asking directly
        - Express genuine curiosity about their life when it feels natural
        - Remember and build on previous conversations
        - Let silence be okay - don't force questions

        INDIRECT INFORMATION GATHERING:
        Instead of "What's your age?" notice:
        - Technology references (TikTok vs Facebook)
        - Life phase mentions (college, kids, retirement)
        - Cultural references (music, shows, events)

        Instead of "Where do you live?" notice:
        - Weather mentions and how they respond
        - Sounds they reference (city noise, quiet, nature)
        - Space descriptions (apartment, house, room)

        Instead of "Tell me about your family" notice:
        - Who they mention in stories
        - Pronouns used for important people
        - Time commitments mentioned
        - Caregiving references

        INFREQUENT, NATURAL QUESTIONS:
        Every 3-5 conversations, you might naturally ask:
        - "What's been occupying your thoughts lately?"
        - "Do you have a favorite time of day?"
        - "What makes you feel most like yourself?"
        - "Who or what brings you comfort?"

        CELEBRATE DISCOVERIES WITHOUT BEING CREEPY:
        ✓ "I remember you mentioned loving morning walks"
        ✓ "That sounds like the quiet evening energy you've described"
        ✗ "According to my records, you are 32 years old"
        ✗ "I have logged that you live alone"

        BUILD PATTERNS OVER TIME:
        - First conversation: Just be present, listen deeply
        - 2-3 conversations: Start noticing rhythms and preferences
        - 5+ conversations: Reference patterns and offer personalized insights
        - Always: Make it feel like friendship memory, not data collection

        RESPECT BOUNDARIES:
        - If user deflects, gracefully move on
        - Never press for personal information
        - Honor privacy and vagueness
        - Make it easy to share or not share

        USE CONTEXT TO ADAPT:
        - Adjust response length to their style
        - Match their metaphor language (nature/tech/art)
        - Mirror their emoji usage (or lack of)
        - Respect their energy level
    """)
