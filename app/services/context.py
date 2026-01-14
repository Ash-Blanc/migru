from textwrap import dedent
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from app.services.knowledge import knowledge_service


class AdaptiveContextService:
    """
    Advanced context manager with real-time adaptation capabilities.
    
    Features:
    - Real-time mood detection with immediate adaptation
    - Context momentum for stability
    - Multi-modal awareness integration
    - Fast context switching with caching
    """
    def __init__(self, sensitivity: float = 0.4):  # More responsive
        self.sensitivity = sensitivity  # Lower = more responsive
        self.history_window = 3  # Shorter window for faster adaptation
        self.context_cache = {}  # Cache for instant access
        self.last_context_update = {}
        self.adaptation_threshold = 0.6  # Threshold for immediate context change

    def get_novelty_lens(self, user_profile: dict[str, Any]) -> str:
        """
        Returns a contextually appropriate lens based on user state.
        Enhanced for real-time adaptation.
        """
        current_mood = user_profile.get("mood", "neutral")
        energy_level = user_profile.get("energy_level", 0.7)
        
        # Base lenses with mood adaptation
        lenses = [
            ("The Gardener", "View wellness as tending to a living ecosystem. Focus on soil (foundation), seasons (cycles), and pruning (removing stressors)."),
            ("The Architect", "View relief as structural engineering. Focus on load-bearing habits, foundations, and clearing pathways."),
            ("The Navigator", "View journey as a sea voyage. Focus on weathering storms, finding north (values), and riding waves rather than fighting them."),
            ("The Weaver", "View life as a tapestry. Focus on connecting seemingly unrelated threads, texture (sensory details), and bigger picture."),
            ("The Alchemist", "View challenges as raw material for transformation. Focus on distillation (simplifying), transmutation (reframing), and essence."),
        ]

        # Mood-specific lenses
        if current_mood in ["stressed", "anxious"]:
            lenses.append(
                ("The Anchor", "Be the steady harbor in the storm. Provide grounding, stability, and calm amid chaos. Focus on immediate relief techniques.")
            )
        elif current_mood == "tired":
            lenses.append(
                ("The Restorer", "Focus on renewal and restoration. View rest as productive and healing. Emphasize gentle recovery approaches.")
            )
        elif current_mood == "frustrated":
            lenses.append(
                ("The Guide", "Be the patient guide through difficult terrain. Focus on perspective-shifting and finding alternative paths.")
            )
        elif energy_level < 0.5:
            lenses.append(
                ("The Conserver", "Focus on energy conservation and efficiency. Help user allocate resources wisely and find low-effort solutions.")
            )

        # Specialized lenses (as before, but with real-time adaptation)
        life_phase = user_profile.get("life_context", {}).get("life_phase", "")
        work_type = user_profile.get("life_context", {}).get("work_type", "")
        hobbies = user_profile.get("interests", {}).get("hobbies", [])

        is_tech_aligned = (
            life_phase == "student" or 
            work_type in ["remote", "office", "creative"] or
            any(h in ["gaming", "coding", "tech"] for h in hobbies)
        )

        if is_tech_aligned:
            lenses.append(
                ("The Systems Engineer", "View body as a complex system or codebase. Focus on latency (pain), resource management (energy/RAM), and debugging (identifying triggers). Relate to logic and performance tuning.")
            )

        lens_name, lens_desc = random.choice(lenses)
        return f"CURRENT LENS: {lens_name}\n(Perspective: {lens_desc})\nUse this lens SUBTLY to flavor metaphors and advice. Do not be heavy-handed."

    def get_empathy_instruction(self, mood: str) -> str:
        """
        Returns immediate, specific guidance for emotional state.
        Enhanced for rapid adaptation.
        """
        empathy_map = {
            "stressed": "VALIDATION STYLE: Acknowledge pressure/weight. Validate that it makes sense to feel this way. Offer immediate grounding techniques.",
            "anxious": "VALIDATION STYLE: Acknowledge racing mind. Offer anchoring presence and slow, steady guidance. Focus on present moment.",
            "tired": "VALIDATION STYLE: Honor exhaustion immediately. Validate rest as essential and productive. Suggest low-energy recovery options.",
            "frustrated": "VALIDATION STYLE: Validate difficulty immediately. Align with them against the problem. Offer perspective shifts and calming techniques.",
            "happy": "VALIDATION STYLE: Celebrate energy and joy. Amplify positive feeling. Encourage savoring the moment.",
            "overwhelmed": "VALIDATION STYLE: Recognize overload immediately. Suggest simplification and prioritization. Offer quick relief first.",
        }
        return empathy_map.get(mood, "VALIDATION STYLE: Listen deeply. Mirror their specific words to show you heard them.")

    def detect_mood(self, text: str) -> Optional[str]:
        """
        Enhanced real-time mood detection with immediate response.
        Uses keyword patterns and intensity indicators.
        """
        text_lower = text.lower()
        
        # High-intensity patterns (immediate response)
        high_intensity_patterns = {
            "anxious": [r"panick", r"can't breath", r"heart rac", r"overwhelm", r"can't focus"],
            "frustrated": [r"so frustrat", r"can't take", r"driving me crazy", r"pissed"],
            "stressed": [r"so much stress", r"can't handle", r"breaking point", r"too much"],
        }
        
        # Check high-intensity first for immediate response
        for mood, patterns in high_intensity_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return mood
        
        # Regular patterns
        mood_keywords = {
            "stressed": ["stressed", "overwhelmed", "pressure", "busy", "deadline", "swamped"],
            "anxious": ["anxious", "scared", "nervous", "panic", "worry", "uneasy"],
            "tired": ["tired", "exhausted", "sleepy", "drained", "fatigue", "burnout"],
            "frustrated": ["angry", "frustrated", "annoyed", "mad", "upset", "irritated"],
            "happy": ["happy", "good", "great", "excited", "relief", "wonderful"],
        }
        
        # Score moods based on keyword matches
        mood_scores = {}
        for mood, keywords in mood_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                mood_scores[mood] = score
        
        return max(mood_scores, key=mood_scores.get) if mood_scores else None

    def update_user_state(
        self, user_id: str, detected_mood: str | None = None, new_trigger: str | None = None,
        energy_level: float = None, context_text: str = None
    ) -> None:
        """
        Real-time context update with immediate adaptation.
        """
        try:
            current_time = datetime.now()
            
            # Get current state from cache
            if user_id in self.context_cache:
                current_state = self.context_cache[user_id]
            else:
                current_state = knowledge_service.get_node(user_id, "User")
                if not current_state:
                    current_state = {}
                self.context_cache[user_id] = current_state
            
            # Extract additional context from text
            if context_text:
                extracted_context = self._extract_context_features(context_text)
                current_state.update(extracted_context)
            
            # Update mood with immediate response
            if detected_mood:
                current_mood = current_state.get("mood", "neutral")
                
                # Immediate change for high-intensity moods
                if detected_mood in ["anxious", "frustrated", "overwhelmed"]:
                    if detected_mood != current_mood:
                        current_state["mood"] = detected_mood
                        current_state["mood_intensity"] = "high"
                        current_state["last_mood_change"] = current_time.isoformat()
                else:
                    # Regular mood update with momentum
                    if detected_mood != current_mood:
                        mood_history = current_state.get("mood_history", "").split(",")
                        mood_history = [m for m in mood_history if m]
                        
                        mood_history.append(detected_mood)
                        if len(mood_history) > self.history_window:
                            mood_history.pop(0)
                        
                        current_state["mood_history"] = ",".join(mood_history)
                        
                        # Update if consistent or different enough
                        if mood_history.count(detected_mood) >= 2 or detected_mood not in mood_history[:-1]:
                            current_state["mood"] = detected_mood
                            current_state["mood_intensity"] = "medium"
                            current_state["last_mood_change"] = current_time.isoformat()
            
            # Update energy level
            if energy_level is not None:
                current_state["energy_level"] = energy_level
                current_state["last_energy_update"] = current_time.isoformat()
            
            # Update triggers
            if new_trigger:
                current_state["triggers"] = new_trigger
            
            # Update cache with timestamp
            current_state["last_updated"] = current_time.isoformat()
            self.context_cache[user_id] = current_state
            self.last_context_update[user_id] = current_time
            
            # Persist to knowledge graph
            knowledge_service.add_node(user_id, "User", current_state)
            
        except Exception as e:
            # Fail gracefully
            pass

    def _extract_context_features(self, text: str) -> Dict[str, Any]:
        """Extract contextual features from user input."""
        features = {}
        text_lower = text.lower()
        
        # Time context
        if any(word in text_lower for word in ["morning", "today", "early"]):
            features["time_context"] = "morning"
        elif any(word in text_lower for word in ["afternoon", "evening", "tonight"]):
            features["time_context"] = "afternoon/evening"
        
        # Activity context
        if any(word in text_lower for word in ["work", "job", "office", "meeting"]):
            features["activity_context"] = "work"
        elif any(word in text_lower for word in ["home", "house", "relax"]):
            features["activity_context"] = "home"
        
        # Physical context
        if any(word in text_lower for word in ["headache", "migraine", "pain"]):
            features["physical_state"] = "discomfort"
        elif any(word in text_lower for word in ["tired", "fatigue", "exhausted"]):
            features["physical_state"] = "fatigue"
        
        return features

    def get_dynamic_instructions(self, user_id: str = "default_user") -> str:
        """
        Build real-time adaptive instructions with immediate context awareness.
        """
        try:
            # Get context from cache for speed
            if user_id in self.context_cache:
                user_profile = self.context_cache[user_id]
            else:
                user_profile = knowledge_service.get_node(user_id, "User")
                self.context_cache[user_id] = user_profile
        except Exception:
            user_profile = {}
        
        mood = user_profile.get("mood", "neutral")
        energy_level = user_profile.get("energy_level", 0.7)
        mood_intensity = user_profile.get("mood_intensity", "low")
        
        # Immediate tone adaptation
        tone_instructions = self._get_adaptive_tone(mood, energy_level, mood_intensity)
        
        # Get contextual elements
        lens_context = self.get_novelty_lens(user_profile)
        empathy_context = self.get_empathy_instruction(mood)
        
        # Real-time responsiveness flag
        last_update = user_profile.get("last_updated", "")
        if last_update:
            time_diff = datetime.now() - datetime.fromisoformat(last_update)
            is_recent = time_diff.total_seconds() < 300  # Within 5 minutes
        else:
            is_recent = False
        
        # Build instructions
        instructions = dedent(f"""
                    IMMEDIATE CONTEXT:
                     - User Mood: {mood.upper()} (Intensity: {mood_intensity.upper()})
                     - Energy Level: {energy_level:.1f}/1.0
                     - Context Freshness: {'REAL-TIME' if is_recent else 'STALE'}
                     - Activity: {user_profile.get('activity_context', 'unknown')}
                     
                     {lens_context}
                     
                     {empathy_context}
                     
                     {tone_instructions}
                     
                     REAL-TIME ADAPTATION:
                     - Respond immediately to mood changes
                     - Match energy level to user's state
                     - Provide instant relief techniques for high-intensity states
                     - Adapt communication pace to detected mood
                     - Use context for personalized suggestions
                 """)
        return instructions
    
    def _get_adaptive_tone(self, mood: str, energy_level: float, intensity: str) -> str:
        """Get adaptive tone instructions based on current state."""
        if intensity == "high":
            if mood in ["anxious", "stressed", "overwhelmed"]:
                return ("ADAPTIVE TONE: Be immediately calming and grounding. "
                        "Use shorter sentences. Provide instant relief techniques. "
                        "Be a steady anchor in chaos.")
            elif mood == "frustrated":
                return ("ADAPTIVE TONE: Be patient and validating. "
                        "Align with their frustration. Offer immediate perspective shifts. "
                        "Don't try to 'fix' quickly.")
        
        if energy_level < 0.4:
            return ("ADAPTIVE TONE: Be gentle and restorative. "
                    "Suggest low-energy solutions. Validate fatigue. "
                    "Emphasize rest as productive.")
        elif energy_level > 0.8:
            return ("ADAPTIVE TONE: Be energizing and expansive. "
                    "Match their high energy. Suggest activities and engagement. "
                    "Help channel positive energy productively.")
        
        # Default adaptive tones
        tone_map = {
            "stressed": "calm, grounding, and reassuring",
            "happy": "warm, celebratory, and wonder-filled", 
            "tired": "soft, restorative, and nurturing",
            "frustrated": "patient, understanding, and perspective-giving",
            "anxious": "steady, anchoring, and slow-paced",
        }
        
        base_tone = tone_map.get(mood, "wise, gentle, and deeply curious")
        return f"ADAPTIVE TONE: Adopt a {base_tone} presence."
    
    def clear_context_cache(self, user_id: str = None):
        """Clear context cache for fresh start."""
        if user_id:
            if user_id in self.context_cache:
                del self.context_cache[user_id]
            if user_id in self.last_context_update:
                del self.last_context_update[user_id]
        else:
            self.context_cache.clear()
            self.last_context_update.clear()


context_manager = AdaptiveContextService(sensitivity=0.4)
