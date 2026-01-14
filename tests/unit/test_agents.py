"""Unit tests for new agent architecture."""

import pytest
from unittest.mock import Mock, patch

from app.agents import migru_core, AgentMode, MigruCore, create_research_agent, create_migru_agent


class TestAgentModes:
    """Test agent mode enumeration and routing."""
    
    def test_agent_modes_exist(self):
        """Test that all agent modes are defined."""
        assert AgentMode.COMPANION
        assert AgentMode.RESEARCHER
        assert AgentMode.ADVISOR
    
    def test_agent_mode_values(self):
        """Test agent mode string values."""
        assert AgentMode.COMPANION.value == "companion"
        assert AgentMode.RESEARCHER.value == "researcher"
        assert AgentMode.ADVISOR.value == "advisor"


class TestMigruCore:
    """Test the core Migru system."""
    
    def test_migru_core_initialization(self):
        """Test Migru core initializes correctly."""
        core = MigruCore()
        
        # Should have all three agents
        assert AgentMode.COMPANION in core._agents
        assert AgentMode.RESEARCHER in core._agents
        assert AgentMode.ADVISOR in core._agents
    
    def test_current_mode_default(self):
        """Test default current mode is companion."""
        core = MigruCore()
        assert core.get_current_mode() == AgentMode.COMPANION
    
    def test_switch_mode(self):
        """Test manual mode switching."""
        core = MigruCore()
        
        # Switch to researcher
        core.switch_mode(AgentMode.RESEARCHER)
        assert core.get_current_mode() == AgentMode.RESEARCHER
        
        # Switch to advisor
        core.switch_mode(AgentMode.ADVISOR)
        assert core.get_current_mode() == AgentMode.ADVISOR
    
    def test_switch_mode_invalid(self):
        """Test switching to invalid mode raises error."""
        core = MigruCore()
        
        with pytest.raises(ValueError):
            core.switch_mode("invalid_mode")


class TestQueryRouting:
    """Test intelligent query routing."""
    
    def test_route_research_queries(self):
        """Test research queries route to researcher."""
        core = MigruCore()
        
        research_queries = [
            "research magnesium for migraines",
            "find studies about migraine triggers",
            "what is the mechanism of migraines",
            "define prodrome phase",
            "search for latest migraine treatments",
        ]
        
        for query in research_queries:
            mode = core.route_query(query)
            assert mode == AgentMode.RESEARCHER, f"Failed for: {query}"
    
    def test_route_advisor_queries(self):
        """Test practical guidance queries route to advisor."""
        core = MigruCore()
        
        advisor_queries = [
            "how do i prevent migraines",
            "help me create a routine",
            "what should i try for relief",
            "recommend a protocol for stress",
            "guide me through managing triggers",
        ]
        
        for query in advisor_queries:
            mode = core.route_query(query)
            assert mode == AgentMode.ADVISOR, f"Failed for: {query}"
    
    def test_route_companion_queries(self):
        """Test emotional support queries route to companion."""
        core = MigruCore()
        
        companion_queries = [
            "I have a terrible headache",
            "feeling really stressed today",
            "my head hurts so much",
            "I'm anxious about this pain",
            "hi",
            "hello",
        ]
        
        for query in companion_queries:
            mode = core.route_query(query)
            assert mode == AgentMode.COMPANION, f"Failed for: {query}"
    
    def test_route_short_messages_to_companion(self):
        """Test short messages default to companion."""
        core = MigruCore()
        
        short_messages = ["hi", "hello", "help", "ok", "thanks"]
        
        for msg in short_messages:
            mode = core.route_query(msg)
            assert mode == AgentMode.COMPANION


class TestAgentCreation:
    """Test agent creation functions."""
    
    def test_create_companion_agent(self):
        """Test companion agent creation."""
        core = MigruCore()
        agent = core._agents[AgentMode.COMPANION]
        
        assert agent is not None
        assert agent.name == "Migru Companion"
        assert "Migru" in agent.instructions
        assert "compassionate" in agent.instructions.lower()
    
    def test_create_researcher_agent(self):
        """Test researcher agent creation."""
        core = MigruCore()
        agent = core._agents[AgentMode.RESEARCHER]
        
        assert agent is not None
        assert agent.name == "Migru Researcher"
        assert "research" in agent.instructions.lower()
        assert len(agent.tools) > 0  # Should have search tools
    
    def test_create_advisor_agent(self):
        """Test advisor agent creation."""
        core = MigruCore()
        agent = core._agents[AgentMode.ADVISOR]
        
        assert agent is not None
        assert agent.name == "Migru Advisor"
        assert "practical" in agent.instructions.lower()


class TestInstructions:
    """Test agent instruction content."""
    
    def test_companion_instructions_structure(self):
        """Test companion instructions have correct structure."""
        core = MigruCore()
        instructions = core._get_companion_instructions()
        
        # Check for key sections
        assert "Migru" in instructions
        assert "Core Identity" in instructions
        assert "Therapeutic Presence" in instructions
        assert "Dynamic Response Patterns" in instructions
    
    def test_researcher_instructions_structure(self):
        """Test researcher instructions have correct structure."""
        core = MigruCore()
        instructions = core._get_researcher_instructions()
        
        # Check for key sections
        assert "Migru Research" in instructions
        assert "Mission" in instructions
        assert "Research Priorities" in instructions
        assert "Response Format" in instructions
    
    def test_advisor_instructions_structure(self):
        """Test advisor instructions have correct structure."""
        core = MigruCore()
        instructions = core._get_advisor_instructions()
        
        # Check for key sections
        assert "Migru Advisor" in instructions
        assert "Role" in instructions
        assert "Protocol Format" in instructions


class TestLegacyCompatibility:
    """Test backward compatibility with legacy functions."""
    
    def test_create_migru_agent_legacy(self):
        """Test legacy create_migru_agent function."""
        agent = create_migru_agent()
        assert agent is not None
        assert agent.name == "Migru Companion"
    
    def test_create_research_agent_legacy(self):
        """Test legacy create_research_agent function."""
        agent = create_research_agent()
        assert agent is not None
        assert agent.name == "Migru Researcher"
    
    def test_migru_core_global_instance(self):
        """Test global migru_core instance exists."""
        from app.agents import migru_core as global_core
        assert global_core is not None
        assert isinstance(global_core, MigruCore)


class TestAgentRun:
    """Test agent run method."""
    
    @patch.object(MigruCore, 'route_query')
    def test_run_uses_routing(self, mock_route):
        """Test run method uses query routing."""
        mock_route.return_value = AgentMode.COMPANION
        
        core = MigruCore()
        
        # Mock the agent run method to avoid actual API calls
        with patch.object(core._agents[AgentMode.COMPANION], 'run', return_value="response"):
            result = core.run("test query", stream=False)
            
            mock_route.assert_called_once_with("test query")
            assert result == "response"
    
    @patch.object(MigruCore, 'route_query')
    def test_run_fallback_on_error(self, mock_route):
        """Test run falls back to companion on error."""
        mock_route.return_value = AgentMode.RESEARCHER
        
        core = MigruCore()
        
        # Make researcher fail, companion succeed
        with patch.object(core._agents[AgentMode.RESEARCHER], 'run', side_effect=Exception("API Error")):
            with patch.object(core._agents[AgentMode.COMPANION], 'run', return_value="fallback response"):
                result = core.run("test query", stream=False)
                
                # Should fall back to companion
                assert result == "fallback response"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
