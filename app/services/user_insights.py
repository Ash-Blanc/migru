"""
User insights tracking and pattern recognition.

This service analyzes conversations to extract meaningful patterns
and insights about the user's life, preferences, and wellness journey.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import re
from app.logger import get_logger
from app.personalization import UserProfile, PersonalizationEngine
from app.db import db

logger = get_logger("migru.insights")


class InsightExtractor:
    """Extract structured insights from natural conversation."""

    def __init__(self):
        self.personalization = PersonalizationEngine(db)

    def extract_from_message(
        self, user_id: str, message: str, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract insights from a user message.
        
        Returns structured information that can be stored in user profile.
        """
        insights = {
            "age_hints": self._extract_age_hints(message),
            "location_hints": self._extract_location_hints(message),
            "schedule_hints": self._extract_schedule_hints(message),
            "interests": self._extract_interests(message),
            "relationships": self._extract_relationships(message),
            "sensitivities": self._extract_sensitivities(message),
            "wellness_patterns": self._extract_wellness_patterns(message),
            "communication_style": self._extract_communication_style(message),
        }

        # Filter out empty insights
        insights = {k: v for k, v in insights.items() if v}

        if insights:
            logger.debug(f"Extracted insights for {user_id}: {list(insights.keys())}")

        return insights

    def _extract_age_hints(self, message: str) -> Optional[Dict[str, str]]:
        """Extract age-related hints from message."""
        message_lower = message.lower()

        # College/university mentions
        if any(word in message_lower for word in ["college", "university", "semester", "dorm"]):
            return {"age_range": "late teens/early 20s", "life_phase": "student"}

        # Career mentions
        if any(word in message_lower for word in ["career", "promotion", "9-5", "office"]):
            if "first job" in message_lower or "new grad" in message_lower:
                return {"age_range": "early 20s", "life_phase": "early career"}
            return {"age_range": "20s-40s", "life_phase": "professional"}

        # Family/kids mentions
        if any(word in message_lower for word in ["my kids", "my children", "daycare", "soccer practice"]):
            return {"age_range": "30s-50s", "life_phase": "parent"}

        # Retirement mentions
        if any(word in message_lower for word in ["retired", "retirement", "grandkids"]):
            return {"age_range": "60s+", "life_phase": "retired"}

        return None

    def _extract_location_hints(self, message: str) -> Optional[Dict[str, str]]:
        """Extract location/living situation hints."""
        message_lower = message.lower()

        location_type = None
        if any(word in message_lower for word in ["city", "urban", "downtown", "traffic", "subway"]):
            location_type = "urban"
        elif any(word in message_lower for word in ["suburbs", "neighborhood", "quiet street"]):
            location_type = "suburban"
        elif any(word in message_lower for word in ["rural", "countryside", "farm", "acres"]):
            location_type = "rural"

        living_situation = None
        if "roommate" in message_lower:
            living_situation = "roommates"
        elif any(word in message_lower for word in ["alone", "live by myself", "solo"]):
            living_situation = "alone"
        elif any(word in message_lower for word in ["family", "spouse", "partner"]):
            living_situation = "family"
        elif "apartment" in message_lower:
            living_situation = "apartment"
        elif "house" in message_lower:
            living_situation = "house"

        if location_type or living_situation:
            return {k: v for k, v in [("location_type", location_type), ("living_situation", living_situation)] if v}

        return None

    def _extract_schedule_hints(self, message: str) -> Optional[Dict[str, str]]:
        """Extract daily schedule and rhythm hints."""
        message_lower = message.lower()

        work_type = None
        if any(word in message_lower for word in ["remote work", "work from home", "wfh"]):
            work_type = "remote"
        elif any(word in message_lower for word in ["office", "commute", "go to work"]):
            work_type = "office"
        elif any(word in message_lower for word in ["shift work", "night shift", "swing shift"]):
            work_type = "shift_work"
        elif any(word in message_lower for word in ["freelance", "gig", "flexible"]):
            work_type = "flexible"

        schedule = None
        if "9 to 5" in message_lower or "9-5" in message_lower:
            schedule = "9-5"
        elif any(word in message_lower for word in ["night shift", "overnight"]):
            schedule = "night_shift"
        elif "flexible schedule" in message_lower:
            schedule = "flexible"

        wake_time = None
        if any(word in message_lower for word in ["early bird", "morning person", "up at dawn", "6am"]):
            wake_time = "early"
        elif any(word in message_lower for word in ["night owl", "late sleeper", "sleep in"]):
            wake_time = "late"

        if work_type or schedule or wake_time:
            return {k: v for k, v in [("work_type", work_type), ("schedule", schedule), ("wake_time", wake_time)] if v}

        return None

    def _extract_interests(self, message: str) -> Optional[List[str]]:
        """Extract mentioned hobbies and interests."""
        interests = []
        message_lower = message.lower()

        # Hobbies
        hobby_keywords = {
            "reading": ["reading", "books", "novel"],
            "music": ["music", "playlist", "song", "concert"],
            "gaming": ["gaming", "video games", "play games"],
            "cooking": ["cooking", "baking", "recipe"],
            "exercise": ["exercise", "workout", "gym", "running", "yoga"],
            "art": ["painting", "drawing", "art", "creative"],
            "outdoors": ["hiking", "camping", "nature", "outdoors"],
            "crafts": ["crafts", "knitting", "sewing", "diy"],
            "photography": ["photography", "photos", "camera"],
            "writing": ["writing", "journaling", "blog"],
        }

        for hobby, keywords in hobby_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                interests.append(hobby)

        return interests if interests else None

    def _extract_relationships(self, message: str) -> Optional[Dict[str, Any]]:
        """Extract relationship context."""
        message_lower = message.lower()
        relationships = {}

        # Family mentions
        if any(word in message_lower for word in ["my family", "parents", "siblings"]):
            relationships["has_family"] = True

        # Partner mentions
        if any(word in message_lower for word in ["partner", "spouse", "husband", "wife", "boyfriend", "girlfriend"]):
            relationships["has_partner"] = True

        # Kids mentions
        if any(word in message_lower for word in ["kids", "children", "son", "daughter"]):
            relationships["has_kids"] = True

        # Pets
        pets = []
        if "dog" in message_lower:
            pets.append("dog")
        if "cat" in message_lower:
            pets.append("cat")
        if pets:
            relationships["pets"] = pets

        # Friends
        if any(word in message_lower for word in ["friends", "hang out", "social"]):
            relationships["has_friends"] = True

        return relationships if relationships else None

    def _extract_sensitivities(self, message: str) -> Optional[Dict[str, Any]]:
        """Extract sensory sensitivities and triggers."""
        message_lower = message.lower()
        sensitivities = {}

        # Weather sensitivity
        if any(word in message_lower for word in ["weather affects", "barometric", "pressure changes"]):
            sensitivities["weather_sensitive"] = True

        # Light sensitivity
        if any(word in message_lower for word in ["bright lights", "light sensitive", "dim lighting"]):
            sensitivities["light_sensitive"] = True

        # Noise sensitivity
        if any(word in message_lower for word in ["loud", "noise sensitive", "quiet space", "need silence"]):
            sensitivities["noise_sensitive"] = True

        # Stress triggers
        triggers = []
        if "deadline" in message_lower:
            triggers.append("deadlines")
        if any(word in message_lower for word in ["crowds", "crowded"]):
            triggers.append("crowds")
        if "conflict" in message_lower:
            triggers.append("conflict")
        if triggers:
            sensitivities["stress_triggers"] = triggers

        return sensitivities if sensitivities else None

    def _extract_wellness_patterns(self, message: str) -> Optional[Dict[str, Any]]:
        """Extract wellness and relief patterns."""
        message_lower = message.lower()
        patterns = {}

        # What helps
        relief_methods = []
        if any(word in message_lower for word in ["walk", "walking"]):
            relief_methods.append("walking")
        if any(word in message_lower for word in ["meditation", "meditate", "mindfulness"]):
            relief_methods.append("meditation")
        if any(word in message_lower for word in ["dark room", "darkness"]):
            relief_methods.append("dark_quiet_space")
        if any(word in message_lower for word in ["music", "sounds"]):
            relief_methods.append("calming_sounds")
        if relief_methods:
            patterns["relief_methods"] = relief_methods

        # Timing patterns
        if any(word in message_lower for word in ["morning", "mornings"]) and any(word in message_lower for word in ["worse", "bad", "difficult"]):
            patterns["morning_difficulty"] = True
        if any(word in message_lower for word in ["evening", "night"]) and any(word in message_lower for word in ["better", "easier"]):
            patterns["evening_improvement"] = True

        return patterns if patterns else None

    def _extract_communication_style(self, message: str) -> Optional[Dict[str, str]]:
        """Extract user's communication preferences."""
        style = {}

        # Message length
        word_count = len(message.split())
        if word_count < 10:
            style["preferred_depth"] = "brief"
        elif word_count < 50:
            style["preferred_depth"] = "moderate"
        else:
            style["preferred_depth"] = "detailed"

        # Emoji usage
        emoji_count = sum(1 for char in message if ord(char) > 127462)
        if emoji_count > 3:
            style["emoji_usage"] = "frequent"
        elif emoji_count > 0:
            style["emoji_usage"] = "moderate"
        else:
            style["emoji_usage"] = "minimal"

        return style if style else None

    def update_user_profile_from_insights(self, user_id: str, insights: Dict[str, Any]) -> bool:
        """Update user profile with extracted insights."""
        try:
            profile_manager = self.personalization.get_user_profile(user_id)
            profile = profile_manager.get_profile()

            # Update age hints
            if "age_hints" in insights:
                age_info = insights["age_hints"]
                if "age_range" in age_info:
                    profile["basics"]["age_range"] = age_info["age_range"]
                if "life_phase" in age_info:
                    profile["life_context"]["life_phase"] = age_info["life_phase"]

            # Update location hints
            if "location_hints" in insights:
                loc_info = insights["location_hints"]
                if "location_type" in loc_info:
                    profile["basics"]["location_type"] = loc_info["location_type"]
                if "living_situation" in loc_info:
                    profile["basics"]["living_situation"] = loc_info["living_situation"]

            # Update schedule hints
            if "schedule_hints" in insights:
                sched_info = insights["schedule_hints"]
                if "work_type" in sched_info:
                    profile["life_context"]["work_type"] = sched_info["work_type"]
                if "schedule" in sched_info:
                    profile["life_context"]["schedule"] = sched_info["schedule"]
                if "wake_time" in sched_info:
                    profile["daily_patterns"]["wake_time"] = sched_info["wake_time"]

            # Update interests (append, don't replace)
            if "interests" in insights:
                current_interests = profile["interests"]["hobbies"]
                for interest in insights["interests"]:
                    if interest not in current_interests:
                        current_interests.append(interest)

            # Update relationships
            if "relationships" in insights:
                rel_info = insights["relationships"]
                if "has_family" in rel_info:
                    profile["relationships"]["support_network"] = "family"
                if "pets" in rel_info:
                    profile["relationships"]["pets"] = rel_info["pets"]

            # Update sensitivities
            if "sensitivities" in insights:
                sens_info = insights["sensitivities"]
                if "weather_sensitive" in sens_info:
                    profile["sensitivities"]["weather_sensitivity"] = "high"
                if "light_sensitive" in sens_info:
                    profile["sensitivities"]["light_sensitivity"] = "high"
                if "noise_sensitive" in sens_info:
                    profile["sensitivities"]["noise_sensitivity"] = "high"
                if "stress_triggers" in sens_info:
                    current_triggers = profile["sensitivities"]["stress_triggers"]
                    for trigger in sens_info["stress_triggers"]:
                        if trigger not in current_triggers:
                            current_triggers.append(trigger)

            # Update wellness patterns
            if "wellness_patterns" in insights:
                wellness_info = insights["wellness_patterns"]
                if "relief_methods" in wellness_info:
                    current_methods = profile["wellness"]["relief_methods"]
                    for method in wellness_info["relief_methods"]:
                        if method not in current_methods:
                            current_methods.append(method)

            # Update communication style
            if "communication_style" in insights:
                comm_info = insights["communication_style"]
                if "preferred_depth" in comm_info:
                    profile["communication"]["preferred_depth"] = comm_info["preferred_depth"]
                if "emoji_usage" in comm_info:
                    profile["communication"]["emoji_usage"] = comm_info["emoji_usage"]

            # Update metadata
            profile["metadata"]["insights_gathered"] += 1
            profile["metadata"]["last_updated"] = datetime.now().isoformat()

            # Save updated profile
            profile_manager.update_profile(profile)
            logger.info(f"Updated profile for {user_id} with {len(insights)} insight categories")
            return True

        except Exception as e:
            logger.error(f"Error updating profile from insights: {e}")
            return False


# Global insight extractor
insight_extractor = InsightExtractor()
