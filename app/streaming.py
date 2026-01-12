"""
Real-time streaming analytics with Pathway for live pattern detection.

This module transforms Migru into a dynamic Real-Time Analyst that:
- Processes conversations as streaming data
- Detects patterns incrementally
- Correlates environmental factors with wellness
- Provides proactive insights
- Maintains warm, caring persona
"""

import json
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import cast

import pathway as pw

from app.logger import get_logger

logger = get_logger("migru.streaming")


class RealtimeWellnessStream:
    """
    Real-time wellness analytics using Pathway's streaming computation.

    Processes user interactions as a continuous stream, detecting patterns
    and correlations incrementally without batch processing delays.
    """

    def __init__(self) -> None:
        self.logger = logger
        self.schema = self._define_schema()

    def _define_schema(self) -> Any:
        """Define Pathway schemas for wellness events."""
        class WellnessEventSchema(pw.Schema):
            user_id: str
            timestamp: str
            event_type: str
            content: str
            metadata: str

        class BiometricEventSchema(pw.Schema):
            user_id: str
            timestamp: str
            heart_rate: int
            sleep_score: int
            step_count: int

        return WellnessEventSchema, BiometricEventSchema

    def create_wellness_stream(self, host: str = "localhost", port: int = 6379, password: str | None = None) -> pw.Table:
        """Create real-time wellness analytics stream connected to Redis."""
        WellnessEventSchema, _ = self.schema
        
        events = pw.io.redis.read_stream(
            host=host,
            port=port,
            password=password,
            stream_keys=["wellness_stream:*"],
            schema=WellnessEventSchema,
            autocommit_duration_ms=50,
            beginning=True
        )

        events = events.with_columns(
            parsed_time=pw.this.timestamp.dt.strptime("%Y-%m-%dT%H:%M:%S"),
            parsed_metadata=cast(Any, pw.this.metadata).json.parse(),
        )
        return events  # type: ignore

    def create_biometric_stream(self, host: str = "localhost", port: int = 6379, password: str | None = None) -> pw.Table:
        """Create simulated biometric data stream (Heart Rate, Sleep)."""
        _, BiometricEventSchema = self.schema
        
        # In a real app, this would read from a different Redis key populated by wearables
        # For now, we simulate or read from a placeholder key
        events = pw.io.redis.read_stream(
            host=host,
            port=port,
            password=password,
            stream_keys=["biometric_stream:*"],
            schema=BiometricEventSchema,
            autocommit_duration_ms=100,
            beginning=True
        )
        
        events = events.with_columns(
             parsed_time=pw.this.timestamp.dt.strptime("%Y-%m-%dT%H:%M:%S")
        )
        return events # type: ignore

    def fuse_streams(self, wellness_events: pw.Table, biometric_events: pw.Table) -> pw.Table:
        """
        Data Fusion: Join conversation events with biometric data.
        
        Correlates what the user SAYS with what their body DOES.
        """
        # Temporal join: Match events within a 5-minute window
        # We want to know: "What was their heart rate when they said 'I feel anxious'?"
        
        fused = wellness_events.windowby(
            pw.this.parsed_time,
            window=pw.temporal.sliding(hop=timedelta(minutes=1), duration=timedelta(minutes=5)),
            behavior=pw.temporal.exactly_once_behavior()
        ).join(
            biometric_events.windowby(
                pw.this.parsed_time,
                window=pw.temporal.sliding(hop=timedelta(minutes=1), duration=timedelta(minutes=5)),
                behavior=pw.temporal.exactly_once_behavior()
            ),
            pw.this.user_id == pw.right.user_id,
            how=pw.JoinMode.LEFT
        ).select(
            user_id=pw.this.user_id,
            content=pw.this.content,
            event_type=pw.this.event_type,
            heart_rate=pw.right.heart_rate,
            timestamp=pw.this.parsed_time
        )
        
        return fused # type: ignore

    def run_analytics_pipeline(self, host: str = "localhost", port: int = 6379, password: str | None = None) -> None:
        """
        Run the full analytics pipeline with Data Fusion and Reactive Alerts.
        """
        # 1. Ingest
        wellness_events = self.create_wellness_stream(host, port, password)
        biometric_events = self.create_biometric_stream(host, port, password)
        
        # 2. Enrich (Model Integration)
        # enriched_events = self.enrich_with_semantics(wellness_events)
        
        # 3. Fuse
        fused_data = self.fuse_streams(wellness_events, biometric_events)
        
        # 4. Analyze (Stateful Computation)
        temporal_patterns = self.detect_temporal_patterns(wellness_events)
        
        # 5. React (Event-driven Architecture)
        self.trigger_reactive_alerts(fused_data, host, port, password)
        
        # 6. Output (Write back to Redis for persistence/dashboarding)
        # pw.io.redis.write_stream(...) 
        
        # Log startup
        self.logger.info("Pathway Analytics Pipeline Initialized (Wellness + Biometrics)")

    def trigger_reactive_alerts(self, fused_stream: pw.Table, host: str, port: int, password: str | None) -> None:
        """
        Generate real-time alerts based on fused data logic.
        
        Example: High Heart Rate + "Anxious" keyword = High Priority Alert
        """
        alerts = fused_stream.filter(
            (pw.this.event_type == "symptom") & 
            (pw.this.heart_rate > 100)
        ).select(
            user_id=pw.this.user_id,
            alert_type=pw.lit("High Physiological Stress"),
            message=pw.lit("User reporting symptoms with elevated heart rate."),
            timestamp=pw.this.timestamp
        )
        
        # Write to Redis Stream for the main agent to consume
        pw.io.redis.write_stream(
            alerts,
            host=host,
            port=port,
            password=password,
            stream_key="migru_alerts",
            maxlen=100
        )

    def detect_temporal_patterns(self, events: pw.Table) -> pw.Table:
        """
        Detect time-based patterns (morning headaches, evening stress, etc.).

        Uses sliding window aggregation for incremental computation.
        """
        # Extract hour from timestamp
        events = events.with_columns(
            hour=pw.this.parsed_time.dt.hour,
            day_of_week=pw.this.parsed_time.dt.dayofweek,  # type: ignore
        )

        # Aggregate symptom patterns by time windows
        # Optimization: Use a 4-hour window with 1-hour hop for faster pattern detection
        hourly_patterns = events.windowby(
            pw.this.parsed_time,
            window=pw.temporal.sliding(
                hop=timedelta(minutes=30),  # More frequent updates
                duration=timedelta(hours=4), # Shorter window for faster convergence
            ),
            behavior=pw.temporal.exactly_once_behavior(),
        ).reduce(
            user_id=pw.this.user_id,
            window_start=pw.this._pw_window_start,
            symptom_count=pw.reducers.count(
                pw.if_(pw.this.event_type == "symptom", 1)  # type: ignore
            ),
            relief_count=pw.reducers.count(pw.if_(pw.this.event_type == "relief", 1)),  # type: ignore
            avg_hour=pw.reducers.avg(pw.this.hour),
        )

        return hourly_patterns  # type: ignore

    def correlate_environment_wellness(self, events: pw.Table) -> pw.Table:
        """
        Correlate environmental factors (weather, activities) with wellness.

        Incremental correlation detection for real-time insights.
        """
        # Extract environmental factors from metadata
        with_env = events.with_columns(
            weather_pressure=pw.this.parsed_metadata.get("weather_pressure"),
            weather_temp=pw.this.parsed_metadata.get("weather_temp"),
            activity=pw.this.parsed_metadata.get("activity"),
            stress_level=pw.this.parsed_metadata.get("stress_level"),
        )

        # Group by user and compute correlations over sliding windows
        correlations = with_env.windowby(
            pw.this.parsed_time,
            window=pw.temporal.sliding(
                hop=timedelta(days=1),
                duration=timedelta(days=7),  # 7-day window
            ),
            behavior=pw.temporal.exactly_once_behavior(),
        ).reduce(
            user_id=pw.this.user_id,
            window_start=pw.this._pw_window_start,
            # Count symptoms by pressure ranges
            low_pressure_symptoms=pw.reducers.count(
                pw.if_(  # type: ignore
                    (pw.this.event_type == "symptom")
                    & (pw.this.weather_pressure < 1010),
                    1,
                )
            ),
            high_pressure_symptoms=pw.reducers.count(
                pw.if_(  # type: ignore
                    (pw.this.event_type == "symptom")
                    & (pw.this.weather_pressure >= 1010),
                    1,
                )
            ),
            # Activity correlations
            activities_during_symptoms=pw.reducers.tuple(
                pw.if_(pw.this.event_type == "symptom", pw.this.activity)  # type: ignore
            ),
        )

        return correlations  # type: ignore

    def detect_trigger_patterns(self, events: pw.Table) -> pw.Table:
        """
        Real-time trigger pattern detection.

        Identifies what precedes symptoms using temporal joins.
        """
        # Separate symptoms and activities
        symptoms = events.filter(pw.this.event_type == "symptom")
        activities = events.filter(pw.this.event_type == "activity")

        # Temporal join: find activities within 2 hours before symptoms
        trigger_candidates = symptoms.join(
            activities,
            symptoms.user_id == activities.user_id,
            how=pw.JoinMode.LEFT,
        ).filter(
            # Activity occurred 0-2 hours before symptom
            (pw.this.parsed_time - pw.right.parsed_time).dt.total_seconds()  # type: ignore
            <= 7200,  # 2 hours
            (pw.this.parsed_time - pw.right.parsed_time).dt.total_seconds() >= 0,  # type: ignore
        )

        # Aggregate potential triggers
        trigger_patterns = trigger_candidates.groupby(
            pw.this.user_id, pw.right.content
        ).reduce(
            user_id=pw.this.user_id,
            potential_trigger=pw.right.content,
            occurrence_count=pw.reducers.count(),
        )

        return trigger_patterns  # type: ignore

    def generate_proactive_insights(
        self, patterns: pw.Table, correlations: pw.Table
    ) -> pw.Table:
        """
        Generate proactive insights from detected patterns.

        Transforms raw patterns into caring, actionable suggestions.
        """
        # Join patterns with correlations
        insights = patterns.join(
            correlations,
            patterns.user_id == correlations.user_id,
            how=pw.JoinMode.LEFT,
        )

        # Generate insight messages based on patterns
        insights = insights.select(
            user_id=pw.this.user_id,
            insight_type=pw.apply(self._classify_insight, pw.this),
            message=pw.apply(self._generate_caring_message, pw.this),
            confidence=pw.apply(self._calculate_confidence, pw.this),
            timestamp=pw.now(),  # type: ignore
        )

        return insights  # type: ignore

    def _classify_insight(self, row: Any) -> str:
        """Classify the type of insight."""
        # This will be replaced with actual logic in real implementation
        if row.symptom_count > 3:
            return "temporal_pattern"
        elif row.low_pressure_symptoms > row.high_pressure_symptoms * 1.5:
            return "weather_correlation"
        return "general_observation"

    def _generate_caring_message(self, row: Any) -> str:
        """Generate warm, caring message from pattern data."""
        # This will be replaced with actual logic in real implementation
        insight_type = self._classify_insight(row)

        messages = {
            "temporal_pattern": "I've noticed a gentle pattern emerging... Your discomfort seems to visit around the same time. Would you like to explore what might be happening during those hours?",
            "weather_correlation": "I'm noticing something curious - when the air pressure drops, you tend to feel more discomfort. The weather might be whispering to us about prevention.",
            "general_observation": "I'm seeing some interesting patterns in our conversations. Would you like to explore them together?",
        }

        return messages.get(insight_type, messages["general_observation"])

    def _calculate_confidence(self, row: Any) -> float:
        """Calculate confidence score for the insight."""
        # Simple confidence based on data points
        if hasattr(row, "symptom_count") and row.symptom_count >= 5:
            return 0.8
        elif hasattr(row, "symptom_count") and row.symptom_count >= 3:
            return 0.6
        return 0.4


class LiveWellnessMonitor:
    """
    Live monitoring service that processes conversation streams in real-time.

    Integrates with Migru's conversation flow to provide:
    - Incremental pattern detection
    - Real-time correlation analysis
    - Proactive wellness insights
    - Low-latency updates
    """

    def __init__(self) -> None:
        self.stream = RealtimeWellnessStream()
        self.event_buffer: list[dict[str, Any]] = []
        self.logger = logger

    def add_conversation_event(
        self,
        user_id: str,
        event_type: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Add conversation event to the real-time stream.

        Args:
            user_id: User identifier
            event_type: Type of event ('message', 'symptom', 'relief', 'activity')
            content: Event content
            metadata: Additional context (weather, time, etc.)
        """
        event = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "content": content,
            "metadata": json.dumps(metadata or {}),
        }

        self.event_buffer.append(event)
        self.logger.debug(f"Added event to stream: {event_type} for {user_id}")

    def extract_event_type(self, message: str) -> str:
        """
        Classify message into event type for stream processing.

        Uses keyword detection to identify:
        - Symptoms (headache, migraine, stress, pain)
        - Relief (better, helped, relieved)
        - Activities (walked, meditated, worked)
        """
        message_lower = message.lower()

        # Symptom indicators
        symptom_keywords = [
            "headache",
            "migraine",
            "pain",
            "stress",
            "anxious",
            "tense",
            "nausea",
            "dizzy",
            "tired",
            "exhausted",
        ]
        if any(keyword in message_lower for keyword in symptom_keywords):
            return "symptom"

        # Relief indicators
        relief_keywords = [
            "better",
            "helped",
            "relieved",
            "improved",
            "feeling good",
            "gone",
            "less pain",
        ]
        if any(keyword in message_lower for keyword in relief_keywords):
            return "relief"

        # Activity indicators
        activity_keywords = [
            "walked",
            "walk",
            "exercise",
            "meditated",
            "ate",
            "slept",
            "worked",
            "meeting",
        ]
        if any(keyword in message_lower for keyword in activity_keywords):
            return "activity"

        return "message"

    def get_recent_insights(self, user_id: str, hours: int = 24) -> list[dict[str, Any]]:
        """
        Get recent insights for a user.

        Args:
            user_id: User identifier
            hours: Look back period in hours

        Returns:
            List of recent insights
        """
        # This will integrate with Pathway's output in real implementation
        # For now, return empty list as placeholder
        self.logger.debug(f"Fetching insights for {user_id} from last {hours} hours")
        return []

    def should_share_insight(self, insight: dict[str, Any]) -> bool:
        """
        Determine if insight should be proactively shared.

        Ensures insights are:
        - High confidence (>0.7)
        - Not shared too frequently (max 1 per day)
        - Genuinely helpful
        - Delivered at appropriate times
        """
        if insight.get("confidence", 0) < 0.7:
            return False

        # Don't overwhelm - max 1 insight per day
        last_insight_time = insight.get("last_shared")
        if last_insight_time:
            time_diff = datetime.now() - datetime.fromisoformat(last_insight_time)
            if time_diff < timedelta(days=1):
                return False

        return True


# Global monitor instance
live_monitor = LiveWellnessMonitor()


def process_message_for_streaming(
    user_id: str, message: str, metadata: dict[str, Any] | None = None
) -> None:
    """
    Process a conversation message for real-time streaming analytics.

    Args:
        user_id: User identifier
        message: User message content
        metadata: Additional context (weather, time, etc.)
    """
    try:
        event_type = live_monitor.extract_event_type(message)
        live_monitor.add_conversation_event(
            user_id=user_id, event_type=event_type, content=message, metadata=metadata
        )
        logger.debug(f"Processed streaming event: {event_type}")
    except Exception as e:
        logger.error(f"Error processing streaming event: {e}")


def get_proactive_insights(user_id: str) -> str | None:
    """
    Get proactive insights if available and appropriate.

    Returns a caring message if patterns warrant sharing, None otherwise.
    """
    try:
        insights = live_monitor.get_recent_insights(user_id, hours=24)

        for insight in insights:
            if live_monitor.should_share_insight(insight):
                return insight.get("message")

        return None
    except Exception as e:
        logger.error(f"Error getting proactive insights: {e}")
        return None
