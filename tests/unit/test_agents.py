"""Unit tests for agents module."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from app.agents import create_research_agent, create_relief_team, create_cerebras_team, create_openrouter_team
from agno.agent import Agent
from agno.team import Team


class TestAgentCreation:
    """Test agent creation functions."""

    @patch('app.agents.Agent')
    def test_create_research_agent_default(self, mock_agent_class):
        """Test research agent creation with default parameters."""
        mock_agent = Mock(spec=Agent)
        mock_agent_class.return_value = mock_agent

        result = create_research_agent()

        mock_agent_class.assert_called_once()
        args, kwargs = mock_agent_class.call_args
        assert kwargs['name'] == "Wisdom Researcher"
        assert 'model' in kwargs

    @patch('app.agents.Agent')
    def test_create_research_agent_custom_model(self, mock_agent_class):
        """Test research agent creation with custom model."""
        mock_agent = Mock(spec=Agent)
        mock_agent_class.return_value = mock_agent

        result = create_research_agent(model="test-model")

        mock_agent_class.assert_called_once()
        args, kwargs = mock_agent_class.call_args
        assert kwargs['model'] == "test-model"

    @patch('app.agents.Agent')
    def test_create_research_agent_minimal_tools(self, mock_agent_class):
        """Test research agent creation with minimal tools."""
        mock_agent = Mock(spec=Agent)
        mock_agent_class.return_value = mock_agent

        result = create_research_agent(minimal_tools=True)

        mock_agent_class.assert_called_once()
        args, kwargs = mock_agent_class.call_args
        # Should only have SmartSearchTools when minimal_tools=True
        assert len(kwargs['tools']) == 1

    @patch('app.agents.Team')
    def test_create_relief_team(self, mock_team_class):
        """Test relief team creation."""
        mock_team = Mock(spec=Team)
        mock_team_class.return_value = mock_team

        result = create_relief_team()

        mock_team_class.assert_called_once()
        args, kwargs = mock_team_class.call_args
        assert kwargs['name'] == "Relief Team"

    @patch('app.agents.Team')
    def test_create_cerebras_team(self, mock_team_class):
        """Test Cerebras team creation."""
        mock_team = Mock(spec=Team)
        mock_team_class.return_value = mock_team

        result = create_cerebras_team()

        mock_team_class.assert_called_once()
        args, kwargs = mock_team_class.call_args
        assert kwargs['name'] == "Cerebras Team"

    @patch('app.agents.Team')
    def test_create_openrouter_team(self, mock_team_class):
        """Test OpenRouter team creation."""
        mock_team = Mock(spec=Team)
        mock_team_class.return_value = mock_team

        result = create_openrouter_team()

        mock_team_class.assert_called_once()
        args, kwargs = mock_team_class.call_args
        assert kwargs['name'] == "OpenRouter Team"


class TestAgentInstructions:
    """Test agent instruction content."""

    def test_research_agent_instructions_content(self):
        """Test research agent instructions contain expected content."""
        from app.agents import create_research_agent

        # Create agent and check instructions
        agent = create_research_agent()
        instructions = agent.instructions

        # Check for key sections
        assert "Wisdom Researcher" in instructions
        assert "CORE RESPONSIBILITIES:" in instructions
        assert "COMMUNICATION STYLE:" in instructions
        assert "SEARCH CAPABILITIES:" in instructions

    def test_research_agent_instructions_minimal_tools(self):
        """Test research agent instructions with minimal tools."""
        from app.agents import create_research_agent

        # Create agent with minimal tools
        agent = create_research_agent(minimal_tools=True)
        instructions = agent.instructions

        # Should contain the same core content
        assert "Wisdom Researcher" in instructions
        assert "CORE RESPONSIBILITIES:" in instructions


class TestAgentTools:
    """Test agent tool configuration."""

    @patch('app.agents.SmartSearchTools')
    @patch('app.agents.YouTubeTools')
    @patch('app.agents.OpenWeatherTools')
    def test_research_agent_tools_complete(self, mock_openweather, mock_youtube, mock_search):
        """Test research agent has all expected tools."""
        mock_search.return_value = Mock()
        mock_youtube.return_value = Mock()
        mock_openweather.return_value = Mock()

        with patch('app.config.config.OPENWEATHER_API_KEY', 'test-key'):
            agent = create_research_agent(minimal_tools=False)

        # Should have all tools
        assert len(agent.tools) >= 2  # SmartSearchTools + YouTubeTools + possibly OpenWeatherTools

    @patch('app.agents.SmartSearchTools')
    def test_research_agent_tools_minimal(self, mock_search):
        """Test research agent has minimal tools."""
        mock_search.return_value = Mock()

        agent = create_research_agent(minimal_tools=True)

        # Should have only SmartSearchTools
        assert len(agent.tools) == 1
        assert isinstance(agent.tools[0], Mock)  # SmartSearchTools mock