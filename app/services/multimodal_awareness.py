"""
Multi-modal awareness for comprehensive context understanding.

This module provides:
- Time-based awareness (circadian rhythms, daily patterns)
- Environmental integration (weather, conditions)
- Pattern recognition across multiple data sources
- Unified awareness engine for proactive adaptation
"""

from datetime import datetime, time as dt_time, timedelta
from typing import Dict, List, Optional, Any, Tuple
import requests
import json

from app.logger import get_logger
from app.config import config

logger = get_logger("migru.multimodal")


class EnvironmentalAwareness:
    """Environmental context awareness including weather and conditions."""

    def __init__(self):
        self.logger = logger
        self.weather_cache = {}
        self.cache_duration_minutes = 30

    def get_current_weather(self, location: str = "default") -> Dict[str, Any]:
        """Get current weather with caching."""
        if not config.OPENWEATHER_API_KEY:
            return {"condition": "unknown", "temperature": "unknown"}

        now = datetime.now()
        cache_key = f"{location}_{now.hour}"

        # Check cache
        if cache_key in self.weather_cache:
            cached_time, cached_data = self.weather_cache[cache_key]
            if (now - cached_time).total_seconds() < self.cache_duration_minutes * 60:
                return cached_data

        try:
            # Get weather (simplified - in real app, use location services)
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": config.OPENWEATHER_API_KEY,
                "units": "metric",
            }

            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                weather_data = {
                    "condition": data["weather"][0]["main"].lower(),
                    "temperature": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "wind_speed": data.get("wind", {}).get("speed", 0),
                    "visibility": data.get("visibility", 10000) / 1000,  # Convert to km
                    "timestamp": now.isoformat(),
                }

                # Cache the result
                self.weather_cache[cache_key] = (now, weather_data)
                return weather_data
            else:
                self.logger.debug(f"Weather API error: {response.status_code}")
                return {"condition": "unknown", "temperature": "unknown"}

        except Exception as e:
            self.logger.debug(f"Weather fetch failed: {e}")
            return {"condition": "unknown", "temperature": "unknown"}

    def get_environmental_insights(self, weather_data: Dict[str, Any]) -> List[str]:
        """Generate wellness insights based on weather conditions."""
        insights = []

        condition = weather_data.get("condition", "unknown")
        temperature = weather_data.get("temperature", 20)
        pressure = weather_data.get("pressure", 1013)

        # Weather-based wellness insights
        if condition in ["rain", "drizzle", "thunderstorm"]:
            insights.append(
                {
                    "type": "weather",
                    "message": "🌧️ Rainy weather can increase headache frequency. Consider staying hydrated and warm.",
                    "confidence": 0.7,
                    "suggestions": [
                        "warm drinks",
                        "gentle movement",
                        "indoor activities",
                    ],
                }
            )
        elif condition in ["clear", "sunny"]:
            if temperature > 25:
                insights.append(
                    {
                        "type": "weather",
                        "message": "☀️ Hot, sunny weather - stay cool and hydrated to prevent heat-related discomfort.",
                        "confidence": 0.8,
                        "suggestions": [
                            "cool environment",
                            "hydration",
                            "sun protection",
                        ],
                    }
                )
        elif condition in ["clouds", "mist", "fog"]:
            insights.append(
                {
                    "type": "weather",
                    "message": "☁️ Overcast conditions can affect mood. Consider bright light or gentle exercise.",
                    "confidence": 0.6,
                    "suggestions": ["light therapy", "movement", "mood support"],
                }
            )

        # Pressure-based insights
        if pressure:
            if pressure < 1000:  # Low pressure
                insights.append(
                    {
                        "type": "pressure",
                        "message": "📉 Low barometric pressure detected. This can trigger migraines for some people.",
                        "confidence": 0.6,
                        "suggestions": [
                            "preventive measures",
                            "stress reduction",
                            "monitor symptoms",
                        ],
                    }
                )
            elif pressure > 1020:  # High pressure
                insights.append(
                    {
                        "type": "pressure",
                        "message": "📈 High pressure system. Changes in pressure may affect wellbeing.",
                        "confidence": 0.5,
                        "suggestions": [
                            "awareness",
                            "gentle routine",
                            "monitor patterns",
                        ],
                    }
                )

        return insights


class TemporalAwareness:
    """Advanced time and circadian rhythm awareness."""

    def __init__(self):
        self.logger = logger

        # Circadian rhythm phases
        self.circadian_phases = {
            "deep_night": (dt_time(0, 0), dt_time(4, 0)),
            "early_morning": (dt_time(4, 0), dt_time(7, 0)),
            "morning_peak": (dt_time(7, 0), dt_time(10, 0)),
            "midday": (dt_time(10, 0), dt_time(14, 0)),
            "afternoon_dip": (dt_time(14, 0), dt_time(17, 0)),
            "evening": (dt_time(17, 0), dt_time(21, 0)),
            "night_winddown": (dt_time(21, 0), dt_time(23, 59)),
        }

        # Daily wellness rhythm
        self.daily_rhythm = {
            "waking_window": (dt_time(5, 0), dt_time(8, 0)),
            "productivity_window": (dt_time(9, 0), dt_time(12, 0)),
            "post_lunch_window": (dt_time(13, 0), dt_time(15, 0)),
            "afternoon_focus": (dt_time(15, 30), dt_time(17, 30)),
            "winddown_window": (dt_time(20, 0), dt_time(23, 0)),
        }

        # Weekly patterns
        self.weekly_patterns = {
            "monday_morning": ["high_stress", "transition"],  # Weekend to work
            "wednesday_afternoon": ["energy_dip", "midweek"],
            "friday_evening": ["anticipation", "transition"],  # Work to weekend
            "sunday_evening": ["anticipatory_stress"],  # Pre-work anxiety
        }

    def get_current_phase(self) -> Tuple[str, Dict[str, Any]]:
        """Get current circadian phase with properties."""
        current_time = datetime.now().time()

        for phase, (start, end) in self.circadian_phases.items():
            if start <= current_time < end:
                phase_properties = self._get_phase_properties(phase)
                return phase, phase_properties

        return "unknown", {}

    def _get_phase_properties(self, phase: str) -> Dict[str, Any]:
        """Get properties of a circadian phase."""
        properties = {
            "deep_night": {
                "energy_level": 0.2,
                "cognitive_performance": 0.3,
                "optimal_for": ["sleep", "rest", "recovery"],
                "avoid": ["important_decisions", "complex_tasks"],
                "hormonal_state": "melatonin_high",
            },
            "early_morning": {
                "energy_level": 0.4,
                "cognitive_performance": 0.6,
                "optimal_for": ["gentle_wakeup", "planning", "light_exercise"],
                "avoid": ["intense_work", "stressful_tasks"],
                "hormonal_state": "cortisol_rising",
            },
            "morning_peak": {
                "energy_level": 0.9,
                "cognitive_performance": 0.9,
                "optimal_for": ["focused_work", "important_tasks", "decisions"],
                "avoid": ["relaxation", "breaks"],
                "hormonal_state": "optimal",
            },
            "midday": {
                "energy_level": 0.8,
                "cognitive_performance": 0.8,
                "optimal_for": ["collaboration", "meetings", "moderate_tasks"],
                "avoid": ["intense_focus", "creative_work"],
                "hormonal_state": "stable",
            },
            "afternoon_dip": {
                "energy_level": 0.5,
                "cognitive_performance": 0.6,
                "optimal_for": ["light_tasks", "breaks", "movement"],
                "avoid": ["complex_decisions", "stressful_work"],
                "hormonal_state": "post_lunch_dip",
            },
            "evening": {
                "energy_level": 0.7,
                "cognitive_performance": 0.7,
                "optimal_for": ["reflection", "planning", "social_time"],
                "avoid": ["intense_work", "important_decisions"],
                "hormonal_state": "winding_down",
            },
            "night_winddown": {
                "energy_level": 0.3,
                "cognitive_performance": 0.4,
                "optimal_for": ["relaxation", "reading", "sleep_preparation"],
                "avoid": ["screens", "stimulating_content", "work"],
                "hormonal_state": "melatonin_rising",
            },
        }

        return properties.get(phase, {})

    def get_temporal_insights(
        self, user_id: str, user_history: List[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Generate insights based on time patterns."""
        insights = []

        current_time = datetime.now()
        current_phase, phase_props = self.get_current_phase()

        # Phase-specific insights
        if phase_props.get("energy_level", 0.5) < 0.4:
            insights.append(
                {
                    "type": "circadian",
                    "message": "🌙 Your body is in a low-energy phase naturally. Be gentle with yourself.",
                    "confidence": 0.8,
                    "suggestions": phase_props.get("optimal_for", ["rest"]),
                }
            )
        elif current_phase == "afternoon_dip":
            insights.append(
                {
                    "type": "circadian",
                    "message": "🌊 Afternoon energy dip is normal. Consider a gentle break or movement.",
                    "confidence": 0.7,
                    "suggestions": ["break", "stretch", "light_tasks"],
                }
            )

        # Day of week insights
        day_of_week = current_time.strftime("%A").lower()
        weekday_pattern = f"{day_of_week}_morning"
        if current_time.hour < 12 and weekday_pattern in self.weekly_patterns:
            patterns = self.weekly_patterns[weekday_pattern]
            if "high_stress" in patterns:
                insights.append(
                    {
                        "type": "weekly_pattern",
                        "message": "⚠️ Monday mornings can be stressful. Consider extra self-care today.",
                        "confidence": 0.6,
                        "suggestions": [
                            "gentle_start",
                            "stress_management",
                            "prioritization",
                        ],
                    }
                )

        return insights


class PatternAwareness:
    """Multi-source pattern recognition and integration."""

    def __init__(self):
        self.logger = logger
        self.pattern_window_days = 14
        self.min_pattern_occurrences = 3

    def detect_temporal_patterns(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect time-based patterns from user events."""
        patterns = {
            "hourly_distribution": {},
            "daily_distribution": {},
            "weekly_distribution": {},
            "peak_times": [],
            "trough_times": [],
        }

        for event in events:
            try:
                event_time = datetime.fromisoformat(event.get("timestamp", ""))
            except (ValueError, TypeError):
                continue

            # Hourly patterns
            hour = event_time.hour
            patterns["hourly_distribution"][hour] = (
                patterns["hourly_distribution"].get(hour, 0) + 1
            )

            # Daily patterns
            day_of_week = event_time.strftime("%A")
            patterns["daily_distribution"][day_of_week] = (
                patterns["daily_distribution"].get(day_of_week, 0) + 1
            )

            # Weekly patterns
            week_num = event_time.isocalendar()[1]
            patterns["weekly_distribution"][week_num] = (
                patterns["weekly_distribution"].get(week_num, 0) + 1
            )

        # Find peaks and troughs
        hourly_dist = patterns["hourly_distribution"]
        if hourly_dist:
            max_count = max(hourly_dist.values())
            min_count = min(hourly_dist.values())

            patterns["peak_times"] = [
                hour for hour, count in hourly_dist.items() if count == max_count
            ]
            patterns["trough_times"] = [
                hour for hour, count in hourly_dist.items() if count == min_count
            ]

        return patterns

    def detect_trigger_patterns(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect patterns related to triggers and relief methods."""
        trigger_analysis = {
            "common_triggers": {},
            "effective_reliefs": {},
            "trigger_sequences": [],
            "context_correlations": {},
        }

        # Analyze triggers
        triggers = []
        relief_methods = []

        for event in events:
            event_type = event.get("event_type", "")
            content = event.get("content", "").lower()

            # Extract triggers from content
            if event_type in ["symptom_report", "discomfort"]:
                trigger_keywords = [
                    "stress",
                    "work",
                    "screen",
                    "weather",
                    "food",
                    "sleep",
                    "noise",
                ]
                for keyword in trigger_keywords:
                    if keyword in content:
                        triggers.append(keyword)

            # Extract relief methods
            if event_type in ["relief_attempt", "coping_strategy"]:
                relief_keywords = [
                    "breathing",
                    "walk",
                    "rest",
                    "meditation",
                    "medication",
                    "water",
                ]
                for keyword in relief_keywords:
                    if keyword in content:
                        relief_methods.append(keyword)

        # Count patterns
        for trigger in set(triggers):
            trigger_analysis["common_triggers"][trigger] = triggers.count(trigger)

        for relief in set(relief_methods):
            trigger_analysis["effective_reliefs"][relief] = relief_methods.count(relief)

        return trigger_analysis

    def generate_pattern_insights(
        self, temporal_patterns: Dict, trigger_patterns: Dict
    ) -> List[Dict[str, Any]]:
        """Generate insights from pattern analysis."""
        insights = []

        # Time-based insights
        peak_times = temporal_patterns.get("peak_times", [])
        if peak_times:
            peak_hours = ", ".join([f"{h:00}" for h in peak_times[:3]])
            insights.append(
                {
                    "type": "temporal_pattern",
                    "message": f"⏰ Your symptoms often peak around {peak_hours}. Consider preventive measures before these times.",
                    "confidence": 0.7,
                    "data": {"peak_times": peak_times},
                }
            )

        # Trigger-based insights
        common_triggers = trigger_patterns.get("common_triggers", {})
        if common_triggers:
            top_trigger = max(common_triggers, key=common_triggers.get)
            insights.append(
                {
                    "type": "trigger_pattern",
                    "message": f"🎯 {top_trigger.title()} appears to be a common trigger. Awareness is the first step.",
                    "confidence": 0.6,
                    "data": {
                        "trigger": top_trigger,
                        "frequency": common_triggers[top_trigger],
                    },
                }
            )

        return insights


class MultiModalAwareness:
    """Unified awareness engine integrating all modalities."""

    def __init__(self):
        self.logger = logger
        self.environmental = EnvironmentalAwareness()
        self.temporal = TemporalAwareness()
        self.patterns = PatternAwareness()

    def get_comprehensive_context(
        self, user_id: str, events: List[Dict] = None, location: str = "default"
    ) -> Dict[str, Any]:
        """Get comprehensive multi-modal context."""
        context = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "environmental": {},
            "temporal": {},
            "patterns": {},
            "insights": [],
        }

        # Environmental context
        weather_data = self.environmental.get_current_weather(location)
        context["environmental"]["weather"] = weather_data
        context["environmental"]["insights"] = (
            self.environmental.get_environmental_insights(weather_data)
        )

        # Temporal context
        current_phase, phase_properties = self.temporal.get_current_phase()
        context["temporal"]["current_phase"] = current_phase
        context["temporal"]["phase_properties"] = phase_properties
        context["temporal"]["insights"] = self.temporal.get_temporal_insights(
            user_id, events
        )

        # Pattern context
        if events:
            temporal_patterns = self.patterns.detect_temporal_patterns(events)
            trigger_patterns = self.patterns.detect_trigger_patterns(events)
            pattern_insights = self.patterns.generate_pattern_insights(
                temporal_patterns, trigger_patterns
            )

            context["patterns"]["temporal"] = temporal_patterns
            context["patterns"]["triggers"] = trigger_patterns
            context["patterns"]["insights"] = pattern_insights

        # Aggregate all insights
        all_insights = (
            context["environmental"]["insights"]
            + context["temporal"]["insights"]
            + context["patterns"].get("insights", [])
        )

        # Sort insights by confidence and relevance
        context["insights"] = sorted(
            all_insights,
            key=lambda x: (x.get("confidence", 0), x.get("type", "")),
            reverse=True,
        )[:5]  # Top 5 insights

        return context

    def get_awareness_summary(self, context: Dict[str, Any]) -> str:
        """Generate human-readable awareness summary."""
        summary_parts = []

        # Environmental summary
        weather = context.get("environmental", {}).get("weather", {})
        if weather.get("condition") != "unknown":
            condition = weather.get("condition", "unknown")
            temp = weather.get("temperature", "N/A")
            summary_parts.append(f"Weather: {condition} at {temp}°C")

        # Temporal summary
        phase = context.get("temporal", {}).get("current_phase", "unknown")
        phase_props = context.get("temporal", {}).get("phase_properties", {})
        energy = phase_props.get("energy_level", 0.5) * 100
        summary_parts.append(
            f"Energy phase: {phase.replace('_', ' ').title()} ({energy:.0f}% energy)"
        )

        # Key insights
        insights = context.get("insights", [])
        if insights:
            top_insight = insights[0]
            summary_parts.append(
                f"Key insight: {top_insight.get('message', 'No insights available')}"
            )

        return " | ".join(summary_parts)


# Global instance
multimodal_awareness = MultiModalAwareness()
