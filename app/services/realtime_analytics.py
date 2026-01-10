"""
Real-time analytics service for continuous wellness pattern detection.

This service provides:
- Continuous pattern monitoring
- Environmental correlation tracking
- Proactive insight generation
- Low-latency updates
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from app.logger import get_logger
from app.db import db
from redis import Redis
from app.config import config

logger = get_logger("migru.realtime")


class PatternDetector:
    """Detect wellness patterns from streaming conversation data."""

    def __init__(self):
        self.redis_client = Redis.from_url(config.REDIS_URL)
        self.logger = logger

    def record_event(
        self,
        user_id: str,
        event_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
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
            self.redis_client.xadd(stream_key, event_data, maxlen=1000)  # Keep last 1000 events
            self.logger.debug(f"Recorded {event_type} event for {user_id}")

            # Update recent patterns
            self._update_recent_patterns(user_id, event_type, metadata)

        except Exception as e:
            self.logger.error(f"Error recording event: {e}")

    def _update_recent_patterns(
        self, user_id: str, event_type: str, metadata: Optional[Dict[str, Any]]
    ):
        """Update incremental pattern statistics."""
        try:
            pattern_key = f"patterns:{user_id}"
            current_hour = datetime.now().hour

            # Get or initialize patterns
            patterns = self.redis_client.hgetall(pattern_key)
            if not patterns:
                patterns = {}

            # Decode bytes to strings if needed
            patterns = {
                k.decode() if isinstance(k, bytes) else k: v.decode()
                if isinstance(v, bytes)
                else v
                for k, v in patterns.items()
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
                self.redis_client.hset(pattern_key, mapping=patterns)

            # Set expiry (30 days)
            self.redis_client.expire(pattern_key, 30 * 24 * 3600)

        except Exception as e:
            self.logger.error(f"Error updating patterns: {e}")

    def get_temporal_patterns(self, user_id: str) -> Dict[str, Any]:
        """
        Get detected temporal patterns for user.
        
        Returns patterns like:
        - Peak symptom hours
        - Day of week patterns
        - Time-based correlations
        """
        try:
            pattern_key = f"patterns:{user_id}"
            patterns = self.redis_client.hgetall(pattern_key)

            if not patterns:
                return {}

            # Decode and parse patterns
            decoded = {
                k.decode() if isinstance(k, bytes) else k: int(v.decode())
                if isinstance(v, bytes)
                else int(v)
                for k, v in patterns.items()
                if k.startswith(b"symptoms_hour") or k == b"symptoms_hour"
            }

            # Find peak hours
            hourly_symptoms = {}
            for key, count in decoded.items():
                if isinstance(key, str) and key.startswith("symptoms_hour_"):
                    hour = int(key.split("_")[-1])
                    hourly_symptoms[hour] = count
                elif isinstance(key, bytes) and key.startswith(b"symptoms_hour_"):
                    hour = int(key.decode().split("_")[-1])
                    hourly_symptoms[hour] = count

            if hourly_symptoms:
                peak_hour = max(hourly_symptoms, key=hourly_symptoms.get)
                return {
                    "peak_hour": peak_hour,
                    "peak_count": hourly_symptoms[peak_hour],
                    "hourly_distribution": hourly_symptoms,
                }

            return {}

        except Exception as e:
            self.logger.error(f"Error getting temporal patterns: {e}")
            return {}

    def get_environmental_correlations(self, user_id: str) -> Dict[str, Any]:
        """
        Get environmental correlations (weather, pressure, etc.).
        
        Returns correlation insights.
        """
        try:
            pattern_key = f"patterns:{user_id}"
            patterns = self.redis_client.hgetall(pattern_key)

            if not patterns:
                return {}

            # Decode patterns
            decoded = {}
            for k, v in patterns.items():
                key = k.decode() if isinstance(k, bytes) else k
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
        self, user_id: str, hours: int = 24, event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent events from stream."""
        try:
            stream_key = f"wellness_stream:{user_id}"
            cutoff_time = datetime.now() - timedelta(hours=hours)
            cutoff_ms = int(cutoff_time.timestamp() * 1000)

            # Read from stream
            events = self.redis_client.xrange(stream_key, min=cutoff_ms)

            # Parse and filter events
            parsed_events = []
            for event_id, event_data in events:
                parsed = {
                    "id": event_id.decode() if isinstance(event_id, bytes) else event_id,
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

    def __init__(self):
        self.detector = PatternDetector()
        self.redis_client = Redis.from_url(config.REDIS_URL)
        self.logger = logger

    def generate_insights(self, user_id: str) -> List[Dict[str, Any]]:
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
                    "message": f"I've been noticing a gentle pattern... Your discomfort tends to visit in the {time_descriptor}. "
                    f"I wonder if we could explore what's happening during those hours? "
                    f"Sometimes understanding the rhythm helps us dance with it better. 🌸",
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
                        "message": "I'm noticing something curious about you and the weather... "
                        "When the air pressure drops, your body seems to whisper that it notices. "
                        "This awareness could help us prepare together. Would you like to explore "
                        "gentle ways to support yourself when pressure changes? 🌤️",
                        "confidence": correlation,
                        "timestamp": datetime.now().isoformat(),
                        "metadata": environmental,
                    }
                )

        return insights

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

    def should_share_now(self, user_id: str, insight: Dict[str, Any]) -> bool:
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
            last_time = datetime.fromisoformat(last_shared.decode())
            time_diff = datetime.now() - last_time

            # Don't share more than once per day
            if time_diff < timedelta(days=1):
                return False

        return True

    def mark_insight_shared(self, user_id: str):
        """Mark that an insight was shared to prevent over-sharing."""
        last_insight_key = f"last_insight:{user_id}"
        self.redis_client.set(
            last_insight_key, datetime.now().isoformat(), ex=7 * 24 * 3600  # 7 days
        )


# Global instances
pattern_detector = PatternDetector()
insight_generator = InsightGenerator()
