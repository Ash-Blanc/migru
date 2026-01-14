"""
Proactive wellness nudge system with temporal intelligence.

This module provides:
- Time-based wellness reminders
- Contextual wellness suggestions
- Intelligent nudge timing and intensity
- Personalized wellness recommendations
"""

import random
from datetime import datetime, time as dt_time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from app.logger import get_logger
from app.services.context import context_manager
from app.ui.theme import Themes

logger = get_logger("migru.nudges")


@dataclass
class WellnessNudge:
    """A wellness nudge with timing and content."""

    id: str
    title: str
    message: str
    nudge_type: str  # "break", "breathing", "posture", "hydration", "stretch"
    intensity: str  # "gentle", "moderate", "strong"
    timing_conditions: Dict[str, Any]
    last_shown: Optional[datetime] = None
    frequency_hours: int = 4
    user_response: Optional[str] = None


class TemporalWellnessEngine:
    """Advanced temporal intelligence for wellness nudges."""

    def __init__(self):
        self.logger = logger
        self.current_date = datetime.now()

        # Time-based wellness periods
        self.wellness_periods = {
            "morning_routine": (dt_time(5, 0), dt_time(9, 0)),
            "mid_morning_break": (dt_time(9, 30), dt_time(10, 30)),
            "lunch_refocus": (dt_time(12, 0), dt_time(13, 0)),
            "afternoon_slump": (dt_time(14, 0), dt_time(16, 0)),
            "evening_winddown": (dt_time(17, 0), dt_time(19, 0)),
            "night_rest": (dt_time(20, 0), dt_time(23, 0)),
        }

        # Circadian rhythm awareness
        self.circadian_phases = {
            "peak_energy": (dt_time(9, 0), dt_time(11, 0)),
            "post_lunch_dip": (dt_time(13, 30), dt_time(15, 0)),
            "second_wind": (dt_time(16, 30), dt_time(18, 0)),
            "melatonin_rise": (dt_time(21, 0), dt_time(23, 0)),
        }

    def get_current_period(self) -> Optional[str]:
        """Get the current wellness period."""
        current_time = datetime.now().time()

        for period, (start, end) in self.wellness_periods.items():
            if start <= current_time <= end:
                return period
        return None

    def get_circadian_phase(self) -> Optional[str]:
        """Get the current circadian phase."""
        current_time = datetime.now().time()

        for phase, (start, end) in self.circadian_phases.items():
            if start <= current_time <= end:
                return phase
        return None

    def calculate_energy_level(self, user_id: str) -> float:
        """Calculate estimated energy level based on time and patterns."""
        current_time = datetime.now().time()
        base_energy = 0.7  # Default baseline

        # Time-based adjustments
        if dt_time(9, 0) <= current_time <= dt_time(11, 0):
            base_energy = 0.9  # Morning peak
        elif dt_time(13, 30) <= current_time <= dt_time(15, 0):
            base_energy = 0.5  # Afternoon dip
        elif dt_time(16, 30) <= current_time <= dt_time(18, 0):
            base_energy = 0.8  # Second wind
        elif current_time >= dt_time(21, 0):
            base_energy = 0.4  # Evening winddown

        # Day of week adjustment
        day_of_week = datetime.now().weekday()
        if day_of_week >= 5:  # Weekend
            base_energy += 0.1

        return min(max(base_energy, 0.2), 1.0)


class ProactiveWellnessNudges:
    """Intelligent wellness nudge system with temporal awareness."""

    def __init__(self):
        self.temporal_engine = TemporalWellnessEngine()
        self.logger = logger

        # Nudge library organized by type and timing
        self.nudge_library = {
            "breathing": {
                "gentle": [
                    "🫁 Take three deep breaths. Notice the air filling your lungs.",
                    "🌊 Follow your breath like waves on the shore. In and out.",
                    "🍃 Breathe in calm, breathe out tension. Simple and effective.",
                ],
                "moderate": [
                    "🧘‍♀️ Try box breathing: 4 counts in, hold 4, out 4, hold 4.",
                    "⚡ 4-7-8 breathing: Inhale 4, hold 7, exhale 8. Instant calm.",
                    "🌸 Alternate nostril breathing for balance and clarity.",
                ],
            },
            "stretch": {
                "gentle": [
                    "🦋 Roll your shoulders slowly. Release the tension.",
                    "🌱 Gently tilt your head from side to side. Neck relief.",
                    "👐 Interlace fingers and stretch forward. Back release.",
                ],
                "moderate": [
                    "🤸‍♀️ Stand up and reach for the sky. Full body stretch.",
                    "🦒 Gentle neck rolls and shoulder shrugs. Desk relief.",
                    "🌿 Seated spinal twist. Refresh your posture.",
                ],
            },
            "posture": [
                "🪑 Sit tall. Shoulders back, chin up. Instant confidence.",
                "📱 Adjust your screen height. Protect your neck.",
                "🦢 Feet flat on floor. Ground yourself for focus.",
            ],
            "hydration": [
                "💧 Take a sip of water. Your brain will thank you.",
                "🌊 Water break time! Hydration fuels clarity.",
                "💦 Your body is asking for water. Listen to it.",
            ],
            "break": {
                "gentle": [
                    "👀 Look away from your screen for 20 seconds. Eye rest.",
                    "🚶‍♀️ Stand up and stretch. Movement is medicine.",
                    "🌺 Step away for a moment. Fresh perspective awaits.",
                ],
                "moderate": [
                    "🌳 5-minute break. Walk around, reset your mind.",
                    "🎵 Put on a favorite song. Quick mood boost.",
                    "🪟 Look out the window. Connect with the world outside.",
                ],
            },
        }

        # Contextual nudge triggers
        self.contextual_triggers = {
            "stress": ["breathing", "gentle"],
            "overwhelm": ["break", "gentle"],
            "tired": ["stretch", "gentle"],
            "focused": ["posture", "hydration"],
            "frustrated": ["breathing", "moderate"],
        }

        # User-specific nudge history
        self.user_nudge_history: Dict[str, List[WellnessNudge]] = {}

    def should_nudge_now(self, user_id: str, user_mood: str = None) -> bool:
        """Determine if a nudge should be shown now."""
        current_time = datetime.now()

        # Check if user was recently nudged
        if user_id in self.user_nudge_history:
            recent_nudges = [
                nudge
                for nudge in self.user_nudge_history[user_id]
                if nudge.last_shown and (current_time - nudge.last_shown).seconds < 3600
            ]
            if len(recent_nudges) >= 2:  # Max 2 nudges per hour
                return False

        # Time-based considerations
        current_period = self.temporal_engine.get_current_period()
        if current_period == "night_rest":
            return False  # Don't nudge during rest time

        # Energy level considerations
        energy_level = self.temporal_engine.calculate_energy_level(user_id)
        if energy_level < 0.3:  # Very low energy - be gentle
            return random.random() < 0.3  # Lower probability

        return random.random() < 0.6  # Base probability

    def generate_contextual_nudge(
        self, user_id: str, user_mood: str = None, context: str = None
    ) -> Optional[WellnessNudge]:
        """Generate a contextual wellness nudge."""
        if not self.should_nudge_now(user_id, user_mood):
            return None

        # Determine nudge type based on context
        nudge_type, intensity = self._select_nudge_type(user_mood, context)

        # Get appropriate nudge content
        nudge_content = self._get_nudge_content(nudge_type, intensity)

        # Create nudge
        nudge = WellnessNudge(
            id=f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M')}",
            title=nudge_content["title"],
            message=nudge_content["message"],
            nudge_type=nudge_type,
            intensity=intensity,
            timing_conditions={
                "period": self.temporal_engine.get_current_period(),
                "energy_level": self.temporal_engine.calculate_energy_level(user_id),
                "circadian_phase": self.temporal_engine.get_circadian_phase(),
            },
            last_shown=datetime.now(),
        )

        # Track nudge
        if user_id not in self.user_nudge_history:
            self.user_nudge_history[user_id] = []
        self.user_nudge_history[user_id].append(nudge)

        return nudge

    def _select_nudge_type(
        self, user_mood: str = None, context: str = None
    ) -> tuple[str, str]:
        """Select appropriate nudge type and intensity."""
        # Mood-based selection
        if user_mood:
            if user_mood in self.contextual_triggers:
                nudge_type, intensity = self.contextual_triggers[user_mood]
                return nudge_type, intensity

        # Context-based selection
        if context:
            if "work" in context.lower() or "desk" in context.lower():
                return "posture", "gentle"
            elif "stress" in context.lower() or "pressure" in context.lower():
                return "breathing", "moderate"
            elif "tired" in context.lower() or "fatigue" in context.lower():
                return "stretch", "gentle"

        # Time-based selection
        current_period = self.temporal_engine.get_current_period()
        if current_period == "mid_morning_break":
            return "break", "gentle"
        elif current_period == "afternoon_slump":
            return "stretch", "moderate"
        elif current_period == "evening_winddown":
            return "breathing", "gentle"

        # Default selection
        return random.choice(["breathing", "posture", "hydration"]), "gentle"

    def _get_nudge_content(self, nudge_type: str, intensity: str) -> Dict[str, str]:
        """Get nudge content based on type and intensity."""
        if nudge_type in ["breathing", "stretch", "break"]:
            messages = self.nudge_library[nudge_type].get(intensity, [])
            if messages:
                message = random.choice(messages)
                return {
                    "title": f"🌸 Gentle {nudge_type.title()} Break",
                    "message": message,
                }
        else:
            messages = self.nudge_library.get(nudge_type, [])
            if messages:
                message = random.choice(messages)
                return {
                    "title": f"💡 {nudge_type.title()} Reminder",
                    "message": message,
                }

        # Fallback
        return {
            "title": "🌸 Wellness Moment",
            "message": "Take a moment to check in with yourself.",
        }

    def get_proactive_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate proactive wellness insights based on patterns."""
        insights = []

        # Time-based insights
        current_period = self.temporal_engine.get_current_period()
        if current_period == "afternoon_slump":
            insights.append(
                {
                    "type": "temporal",
                    "message": "🌊 Afternoon energy dip is natural. Consider a gentle stretch or breathing exercise.",
                    "confidence": 0.8,
                }
            )
        elif current_period == "evening_winddown":
            insights.append(
                {
                    "type": "temporal",
                    "message": "🌙 Evening is approaching. Start winding down for better rest.",
                    "confidence": 0.7,
                }
            )

        # Energy-based insights
        energy_level = self.temporal_engine.calculate_energy_level(user_id)
        if energy_level < 0.5:
            insights.append(
                {
                    "type": "energy",
                    "message": "🔋 Your energy seems lower right now. Be gentle with yourself.",
                    "confidence": 0.6,
                }
            )

        return insights

    def record_user_response(self, user_id: str, nudge_id: str, response: str):
        """Record user response to a nudge for learning."""
        if user_id in self.user_nudge_history:
            for nudge in self.user_nudge_history[user_id]:
                if nudge.id == nudge_id:
                    nudge.user_response = response
                    break


# Global instance
wellness_nudges = ProactiveWellnessNudges()
