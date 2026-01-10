from textwrap import dedent
from app.services.knowledge import knowledge_service

class ContextManager:
    def get_dynamic_instructions(self, user_id: str = "default_user") -> str:
        """
        Builds dynamic instructions based on user profile and state.
        This enables Dynamic Persona Adaptation and Contextual Awareness.
        """
        # Retrieve user profile from Knowledge Graph (simulated)
        user_profile = knowledge_service.get_node(user_id, "User")

        base_tone = "wise, gentle, and deeply curious"
        if user_profile.get("mood") == "stressed":
            base_tone = "calm, grounding, and reassuring"
        elif user_profile.get("mood") == "happy":
            base_tone = "warm, celebratory, and wonder-filled"
        elif user_profile.get("mood") == "tired":
            base_tone = "soft, restorative, and nurturing"
        elif user_profile.get("mood") == "frustrated":
            base_tone = "patient, understanding, and perspective-giving"

        instructions = dedent(f"""
                    CURRENT CONTEXT:
                    - User State: {user_profile.get('mood', 'neutral')}
                    - Notable Patterns: {user_profile.get('triggers', 'still discovering')}
                    - What Has Helped: {user_profile.get('relief_methods', 'learning together')}
                    - Energy Rhythms: {user_profile.get('energy_patterns', 'observing')}
                    - Environmental Sensitivities: {user_profile.get('environmental_factors', 'noticing')}
                    
                    ADAPTATION:
                    - Adopt a {base_tone} presence.
                    - Honor what has worked before: {user_profile.get('relief_methods', 'co-discovering')}.
                    - Stay curious about patterns and connections.
                    - Ask gentle questions that invite reflection.
                    - Share observations without claiming expertise.
                """)
        return instructions

    def update_user_state(
        self, user_id: str, mood: str = None, new_trigger: str = None
    ):
        """Updates the user's state in the Knowledge Graph."""
        updates = {}
        if mood:
            updates["mood"] = mood
        if new_trigger:
            # In a real graph, this would add an edge
            updates["triggers"] = new_trigger

        knowledge_service.add_node(user_id, "User", updates)

context_manager = ContextManager()