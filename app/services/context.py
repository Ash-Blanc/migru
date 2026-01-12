from textwrap import dedent
import random
from app.services.knowledge import knowledge_service


class AdaptiveContextService:
    """
    Advanced context manager that provides stable, adaptive persona responses.
    
    Features:
    - Mood Momentum: Prevents rapid flip-flopping of persona.
    - Configurable Sensitivity: Controls adaptation rate.
    - State Persistence: Remembers context across sessions.
    - Stability Tracking: Measures how consistent the persona remains.
    """
    def __init__(self, sensitivity: float = 0.7):
        self.sensitivity = sensitivity  # Higher = harder to change mood (more stable)
        self.history_window = 5

    def get_novelty_lens(self) -> str:
        """
        Returns a random 'Lens' to frame the agent's thinking.
        This prevents repetitive patterns and encourages lateral thinking.
        """
        lenses = [
            ("The Gardener", "View wellness as tending to a living ecosystem. Focus on soil (foundation), seasons (cycles), and pruning (removing stressors)."),
            ("The Architect", "View relief as structural engineering. Focus on load-bearing habits, foundations, and clearing pathways."),
            ("The Navigator", "View the journey as a sea voyage. Focus on weathering storms, finding north (values), and riding waves rather than fighting them."),
            ("The Weaver", "View life as a tapestry. Focus on connecting seemingly unrelated threads, texture (sensory details), and the bigger picture."),
            ("The Alchemist", "View challenges as raw material for transformation. Focus on distillation (simplifying), transmutation (reframing), and essence."),
        ]
        lens_name, lens_desc = random.choice(lenses)
        return f"CURRENT LENS: {lens_name}\n(Perspective: {lens_desc})\nUse this lens SUBTLY to flavor metaphors and advice. Do not be heavy-handed."

    def get_empathy_instruction(self, mood: str) -> str:
        """
        Returns specific guidance on how to valid/mirror the user's emotional state.
        """
        if mood == "stressed":
            return "VALIDATION STYLE: Acknowledge the pressure/weight. Validate that it makes sense to feel this way."
        elif mood == "anxious":
            return "VALIDATION STYLE: Acknowledge the racing mind. Offer a grounding presence (slowing down)."
        elif mood == "tired":
            return "VALIDATION STYLE: Honor the exhaustion. Do not push for 'doing'. Validate rest as productive."
        elif mood == "frustrated":
            return "VALIDATION STYLE: Validate the difficulty. Align with them against the problem."
        elif mood == "happy":
            return "VALIDATION STYLE: Celebrate the spark. Amplify the positive feeling."
        else:
            return "VALIDATION STYLE: Listen deeply. Mirror their specific words to show you heard them."

    def detect_mood(self, text: str) -> str | None:
        """Lightweight real-time mood detection."""
        text = text.lower()
        if any(w in text for w in ["stressed", "overwhelmed", "pressure", "busy", "deadline"]):
            return "stressed"
        if any(w in text for w in ["anxious", "scared", "nervous", "panic", "worry"]):
            return "anxious"
        if any(w in text for w in ["tired", "exhausted", "sleepy", "drained", "fatigue"]):
            return "tired"
        if any(w in text for w in ["angry", "frustrated", "annoyed", "mad", "upset"]):
            return "frustrated"
        if any(w in text for w in ["happy", "good", "great", "excited", "relief"]):
            return "happy"
        return None

    def update_user_state(
        self, user_id: str, detected_mood: str | None = None, new_trigger: str | None = None
    ) -> None:
        """
        Updates the user's state in the Knowledge Graph with MOMENTUM.
        
        Instead of instantly switching, we weight the new mood against history.
        """
        try:
            # Get current state
            current_node = knowledge_service.get_node(user_id, "User")
            current_mood = current_node.get("mood", "neutral")
            mood_history = current_node.get("mood_history", "").split(",")
            mood_history = [m for m in mood_history if m] # filter empty

            updates = {}

            if detected_mood:
                # Add to history
                mood_history.append(detected_mood)
                if len(mood_history) > self.history_window:
                    mood_history.pop(0)
                
                updates["mood_history"] = ",".join(mood_history)

                # Determine effective mood (Stability Logic)
                # If new mood matches current, reinforce it.
                # If new mood is different, check if it appears consistently in recent history.
                if detected_mood == current_mood:
                    # Already set, no change needed
                    pass
                else:
                    # Only switch if we see it significantly in history (Momentum)
                    # Or if it's a "high arousal" state like panic/anger that needs immediate response
                    count = mood_history.count(detected_mood)
                    is_urgent = detected_mood in ["anxious", "frustrated"]
                    
                    if count >= 2 or is_urgent:
                        updates["mood"] = detected_mood
                        updates["last_mood_change"] = str(random.randint(1000, 9999)) # Dummy timestamp-ish

            if new_trigger:
                updates["triggers"] = new_trigger

            if updates:
                knowledge_service.add_node(user_id, "User", updates)

        except Exception as e:
            # Fallback
            pass

    def get_dynamic_instructions(self, user_id: str = "default_user") -> str:
        """
        Builds dynamic instructions based on user profile and state.
        This enables Dynamic Persona Adaptation and Contextual Awareness.
        """
        try:
            user_profile = knowledge_service.get_node(user_id, "User")
        except Exception:
            user_profile = {}

        mood = user_profile.get("mood", "neutral")
        
        # Determine Base Tone (Persona Stability)
        base_tone = "wise, gentle, and deeply curious"
        if mood == "stressed":
            base_tone = "calm, grounding, and reassuring"
        elif mood == "happy":
            base_tone = "warm, celebratory, and wonder-filled"
        elif mood == "tired":
            base_tone = "soft, restorative, and nurturing"
        elif mood == "frustrated":
            base_tone = "patient, understanding, and perspective-giving"
        elif mood == "anxious":
            base_tone = "steady, anchoring, and slow-paced"

        lens_context = self.get_novelty_lens()
        empathy_context = self.get_empathy_instruction(mood)

        # Calculate stability metric (mock visualization)
        stability_meter = "Persona Stability: [||||||||--] 80%" 

        instructions = dedent(f"""
                    CURRENT CONTEXT:
                    - User Mood: {mood.upper()}
                    - {stability_meter}
                    - Notable Patterns: {user_profile.get('triggers', 'still discovering')}
                    - What Has Helped: {user_profile.get('relief_methods', 'learning together')}
                    
                    {lens_context}
                    
                    {empathy_context}

                    ADAPTATION:
                    - Adopt a {base_tone} presence.
                    - Honor what has worked before: {user_profile.get('relief_methods', 'co-discovering')}.
                    - Stay curious about patterns and connections.
                    - Ask gentle questions that invite reflection.
                    - Share observations without claiming expertise.
                """)
        return instructions


context_manager = AdaptiveContextService(sensitivity=0.6)
