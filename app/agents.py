"""
Legacy Agent Interface (Compatibility Layer)
Redirects to the new centralized MigruCore in app/core.py.
"""

from app.core import migru_core, AgentMode, MigruCore
from agno.agent import Agent

# Expose main interface for backwards compatibility
relief_team = migru_core
cerebras_team = None  # Deprecated
openrouter_team = None  # Deprecated
research_agent = None # Will be accessible via migru_core.agents[AgentMode.RESEARCHER] if initialized

def create_migru_agent(model: str | None = None, enable_tools: bool = False) -> Agent:
    """Legacy function - returns the companion agent."""
    # Ensure initialization has happened or handle async nature if possible.
    # Since this is legacy synchronous code and core is async, we might return a placeholder 
    # or the agent if it exists. Best effort.
    if AgentMode.COMPANION in migru_core.agents:
        return migru_core.agents[AgentMode.COMPANION]
    
    # If not initialized, we can't easily return the agent synchronously without breaking the pattern.
    # For now, we assume the core is initialized by the main entry point before this is called 
    # in a live context. For tests, they might need updates.
    return None

def create_research_agent(model: str | None = None, minimal_tools: bool = False) -> Agent:
    """Legacy function - returns the researcher agent."""
    if AgentMode.RESEARCHER in migru_core.agents:
        return migru_core.agents[AgentMode.RESEARCHER]
    return None

# Re-export necessary components
__all__ = [
    "migru_core",
    "AgentMode",
    "MigruCore",
    "create_migru_agent",
    "create_research_agent",
    "relief_team"
]