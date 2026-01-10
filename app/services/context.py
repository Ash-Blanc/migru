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
        
        base_tone = "warm, cheerful, and cheesy"
        if user_profile.get("mood") == "stressed":
            base_tone = "calm, soothing, and direct"
        elif user_profile.get("mood") == "happy":
            base_tone = "excited, energetic, and playful"
            
        instructions = dedent(f"""
            CURRENT CONTEXT:
            - User Mood: {user_profile.get('mood', 'neutral')}
            - Known Triggers: {user_profile.get('triggers', 'unknown')}
            - Effective Relief: {user_profile.get('relief_methods', 'unknown')}
            
            ADAPTATION:
            - Adopt a {base_tone} tone.
            - Prioritize relief methods that worked previously: {user_profile.get('relief_methods', 'none')}.
        """)
        return instructions

    def update_user_state(self, user_id: str, mood: str = None, new_trigger: str = None):
        """Updates the user's state in the Knowledge Graph."""
        updates = {}
        if mood:
            updates["mood"] = mood
        if new_trigger:
            # In a real graph, this would add an edge
            updates["triggers"] = new_trigger 
            
        knowledge_service.add_node(user_id, "User", updates)

context_manager = ContextManager()
