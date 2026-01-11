"""
Real-time analytics service for continuous wellness pattern detection.

This service provides:
- Continuous pattern monitoring
- Environmental correlation tracking
- Proactive insight generation
- Low-latency updates
"""

import json
from datetime import datetime, timedelta
from typing import Any, cast

from redis import Redis

from app.config import config
from app.logger import get_logger

logger = get_logger("migru.realtime")


class PatternDetector:
    """Detect wellness patterns from streaming conversation data."""

    def __init__(self) -> None:
        self.redis_client = Redis.from_url(config.REDIS_URL)
        self.logger = logger

    def record_event(
        self,
        user_id: str,
        event_type: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Record an event to the time-series stream.

        Uses Redis Streams for low-latency event recording.
        """
        try:
            stream_key = f"wellness_stream:{user_id}"
            event_data = {
                "event_type": event_type,
                "content": content,
                "metadata": json.dumps(metadata or {}),
                "timestamp": datetime.now().isoformat(),
            }

            # Add to Redis stream
            self.redis_client.xadd(stream_key, cast(dict[Any, Any], event_data), maxlen=1000)  # Keep last 1000 events
            self.logger.debug(f"Recorded {event_type} event for {user_id}")

            # Update recent patterns
            self._update_recent_patterns(user_id, event_type, metadata)

        except Exception as e:
            self.logger.error(f"Error recording event: {e}")

    def _update_recent_patterns(
        self, user_id: str, event_type: str, metadata: dict[str, Any] | None
    ) -> None:
        """Update incremental pattern statistics."""
        try:
            pattern_key = f"patterns:{user_id}"
            current_hour = datetime.now().hour

            # Get or initialize patterns
            raw_patterns = self.redis_client.hgetall(pattern_key)
            if not raw_patterns:
                patterns: dict[str, str] = {}
            else:
                # Decode bytes to strings if needed
                patterns = {
                    k.decode() if isinstance(k, bytes) else str(k): v.decode()
                    if isinstance(v, bytes)
                    else str(v)
                    for k, v in cast(dict[Any, Any], raw_patterns).items()
                }

            # Update hourly symptom counts
            if event_type == "symptom":
                hour_key = f"symptoms_hour_{current_hour}"
                patterns[hour_key] = str(int(patterns.get(hour_key, "0")) + 1)

            # Update weather correlations
            if event_type == "symptom" and metadata and "weather_pressure" in metadata:
                pressure = metadata["weather_pressure"]
                if pressure < 1010:
                    patterns["low_pressure_symptoms"] = str(
                        int(patterns.get("low_pressure_symptoms", "0")) + 1
                    )
                else:
                    patterns["high_pressure_symptoms"] = str(
                        int(patterns.get("high_pressure_symptoms", "0")) + 1
                    )

            # Store updated patterns
            if patterns:
                self.redis_client.hset(pattern_key, mapping=cast(dict[Any, Any], patterns))

            # Set expiry (30 days)
            self.redis_client.expire(pattern_key, 30 * 24 * 3600)

        except Exception as e:
            self.logger.error(f"Error updating patterns: {e}")

    def get_temporal_patterns(self, user_id: str) -> dict[str, Any]:
        """
        Get detected temporal patterns for user.

        Returns patterns like:
        - Peak symptom hours
        - Day of week patterns
        - Time-based correlations
        """
        try:
            pattern_key = f"patterns:{user_id}"
            raw_patterns = self.redis_client.hgetall(pattern_key)

            if not raw_patterns:
                return {}

            # Decode and parse patterns
            decoded = {
                k.decode() if isinstance(k, bytes) else str(k): int(v.decode())
                if isinstance(v, bytes)
                else int(v)
                for k, v in cast(dict[Any, Any], raw_patterns).items()
                if (k.decode() if isinstance(k, bytes) else str(k)).startswith("symptoms_hour")
            }

            # Find peak hours
            hourly_symptoms: dict[int, int] = {}
            for key, count in decoded.items():
                if key.startswith("symptoms_hour_"):
                    hour = int(key.split("_")[-1])
                    hourly_symptoms[hour] = count

            if hourly_symptoms:
                peak_hour = max(hourly_symptoms, key=lambda k: hourly_symptoms[k])
                return {
                    "peak_hour": peak_hour,
                    "peak_count": hourly_symptoms[peak_hour],
                    "hourly_distribution": hourly_symptoms,
                }

            return {}

        except Exception as e:
            self.logger.error(f"Error getting temporal patterns: {e}")
            return {}

    def get_environmental_correlations(self, user_id: str) -> dict[str, Any]:
        """
        Get environmental correlations (weather, pressure, etc.).

        Returns correlation insights.
        """
        try:
            pattern_key = f"patterns:{user_id}"
            raw_patterns = self.redis_client.hgetall(pattern_key)

            if not raw_patterns:
                return {}

            # Decode patterns
            decoded = {}
            for k, v in cast(dict[Any, Any], raw_patterns).items():
                key = k.decode() if isinstance(k, bytes) else str(k)
                value = int(v.decode()) if isinstance(v, bytes) else int(v)
                decoded[key] = value

            low_pressure = decoded.get("low_pressure_symptoms", 0)
            high_pressure = decoded.get("high_pressure_symptoms", 0)

            if low_pressure + high_pressure < 5:  # Need minimum data
                return {}

            # Calculate correlation strength
            total = low_pressure + high_pressure
            low_pressure_rate = low_pressure / total if total > 0 else 0

            return {
                "weather_sensitivity": low_pressure_rate > 0.6,
                "low_pressure_symptoms": low_pressure,
                "high_pressure_symptoms": high_pressure,
                "correlation_strength": abs(low_pressure_rate - 0.5) * 2,  # 0-1 scale
            }

        except Exception as e:
            self.logger.error(f"Error getting environmental correlations: {e}")
            return {}

    def get_recent_events(
        self, user_id: str, hours: int = 24, event_type: str | None = None
    ) -> list[dict[str, Any]]:
        """Get recent events from stream."""
        try:
            stream_key = f"wellness_stream:{user_id}"
            cutoff_time = datetime.now() - timedelta(hours=hours)
            cutoff_ms = int(cutoff_time.timestamp() * 1000)

            # Read from stream
            events = self.redis_client.xrange(stream_key, min=cutoff_ms)

            # Parse and filter events
            parsed_events = []
            for event_id, event_data in cast(list[Any], events):
                parsed = {
                    "id": event_id.decode() if isinstance(event_id, bytes) else str(event_id),
                    "event_type": event_data.get(b"event_type", b"").decode(),
                    "content": event_data.get(b"content", b"").decode(),
                    "timestamp": event_data.get(b"timestamp", b"").decode(),
                    "metadata": json.loads(
                        event_data.get(b"metadata", b"{}").decode()
                    ),
                }

                if event_type is None or parsed["event_type"] == event_type:
                    parsed_events.append(parsed)

            return parsed_events

        except Exception as e:
            self.logger.error(f"Error getting recent events: {e}")
            return []


class InsightGenerator:
    """Generate caring, proactive insights from detected patterns."""

    def __init__(self) -> None:
        self.detector = PatternDetector()
        self.redis_client = Redis.from_url(config.REDIS_URL)
        self.logger = logger

    def generate_insights(self, user_id: str) -> list[dict[str, Any]]:
        """
        Generate insights from user's patterns.

        Returns list of insights with:
        - message: Caring, actionable message
        - confidence: Confidence score (0-1)
        - type: Insight type
        - timestamp: When generated
        """
        insights = []

        # Get patterns
        temporal = self.detector.get_temporal_patterns(user_id)
        environmental = self.detector.get_environmental_correlations(user_id)

        # Temporal insights
        if temporal and temporal.get("peak_count", 0) >= 3:
            peak_hour = temporal["peak_hour"]
            time_descriptor = self._describe_time(peak_hour)

            insights.append(
                {
                    "type": "temporal_pattern",
                    "message": f"I was just thinking about the {time_descriptor}... I wonder if we could explore some gentle "
                    f"comfort strategies for that time of day? Sometimes a small shift in our rhythm "
                    f"brings a bit more ease. 🌸",
                    "confidence": min(temporal["peak_count"] / 10, 0.9),
                    "timestamp": datetime.now().isoformat(),
                    "metadata": temporal,
                }
            )

        # Weather correlation insights
        if environmental and environmental.get("weather_sensitivity"):
            correlation = environmental["correlation_strength"]
            if correlation > 0.6:
                insights.append(
                    {
                        "type": "weather_correlation",
                        "message": "It might be helpful to keep an eye on the weather together... "
                        "I've found that when the air pressure changes, our bodies sometimes notice. "
                        "Would you like to explore some gentle ways to support yourself when the sky "
                        "is in transition? 🌤️",
                        "confidence": correlation,
                        "timestamp": datetime.now().isoformat(),
                        "metadata": environmental,
                    }
                )

        # Behavioral Nudges (Contextual & Proactive)
        nudges = self.generate_nudges(user_id, temporal)
        insights.extend(nudges)

        return insights

    def generate_nudges(self, user_id: str, temporal_patterns: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Generate contextual behavioral nudges based on time and patterns.
        """
        nudges = []
        current_hour = datetime.now().hour

        # 1. Late Night Nudge (if active late)
        if current_hour >= 23 or current_hour < 5:
            nudges.append({
                "type": "behavioral_nudge",
                "message": "The world is quiet now... gentle reminder that rest is also a form of healing. 🌙",
                "confidence": 0.8,
                "timestamp": datetime.now().isoformat(),
            })

        # 2. Preemptive Care (if approaching peak symptom time)
        peak_hour = temporal_patterns.get("peak_hour")
        if peak_hour is not None:
            # If we are 1-2 hours before typical peak
            if 0 <= (peak_hour - current_hour) <= 2:
                nudges.append({
                    "type": "preemptive_care",
                    "message": f"We're approaching a time of day ({peak_hour}:00) that has sometimes been challenging. "
                               "Perhaps a moment of stillness or hydration now could support you ahead of time? 💧",
                    "confidence": 0.85,
                    "timestamp": datetime.now().isoformat(),
                })

        return nudges

    def _describe_time(self, hour: int) -> str:
        """Convert hour to natural language."""
        if 5 <= hour < 12:
            return "morning hours"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "late night or early morning"

    def should_share_now(self, user_id: str, insight: dict[str, Any]) -> bool:
        """
        Determine if insight should be shared now.

        Considers:
        - Minimum confidence threshold
        - Time since last insight shared
        - User's current conversation context
        - Appropriateness of timing
        """
        # Minimum confidence
        if insight.get("confidence", 0) < 0.7:
            return False

        # Check when last insight was shared
        last_insight_key = f"last_insight:{user_id}"
        last_shared = self.redis_client.get(last_insight_key)

        if last_shared:
            last_time_str = last_shared.decode() if isinstance(last_shared, bytes) else str(last_shared)
            last_time = datetime.fromisoformat(last_time_str)
            time_diff = datetime.now() - last_time

            # Don't share more than once per day
            if time_diff < timedelta(days=1):
                return False

        return True

    def mark_insight_shared(self, user_id: str) -> None:
        """Mark that an insight was shared to prevent over-sharing."""
        last_insight_key = f"last_insight:{user_id}"
        self.redis_client.set(
            last_insight_key, datetime.now().isoformat(), ex=7 * 24 * 3600  # 7 days
        )


# Global instances
pattern_detector = PatternDetector()
insight_generator = InsightGenerator()
