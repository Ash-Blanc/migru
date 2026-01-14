"""Unit tests for CLI components."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from rich.console import Console

from app.cli.command_palette import CommandPalette, SafePromptSession
from app.cli.session import (
    show_profile,
    show_patterns,
    show_history,
    show_about,
    show_settings,
    handle_model_switch
)


class TestCommandPalette:
    """Test command palette functionality."""

    def test_command_palette_initialization(self):
        """Test command palette initialization."""
        palette = CommandPalette()
        
        # Should have expected commands
        expected_commands = [
            "/help", "/exit", "/clear", "/settings", "/about",
            "/history", "/profile", "/patterns", "/model", "/bio"
        ]
        assert palette.commands == expected_commands
        
        # Should have a base completer
        assert hasattr(palette, 'base_completer')

    def test_command_palette_get_completer(self):
        """Test getting completer from palette."""
        palette = CommandPalette()
        completer = palette.get_completer()
        
        # Should return a conditional completer
        assert hasattr(completer, 'get_completions')


class TestSafePromptSession:
    """Test safe prompt session functionality."""

    def test_safe_prompt_session_initialization(self):
        """Test safe prompt session initialization."""
        session = SafePromptSession()
        
        # Should have style and bindings
        assert hasattr(session, 'style')
        assert hasattr(session, 'bindings')
        assert hasattr(session, 'completer')

    @patch('app.cli.command_palette.PromptSession')
    def test_safe_prompt_session_prompt(self, mock_prompt_session_class):
        """Test safe prompt session prompt method."""
        mock_session = Mock()
        mock_session.prompt.return_value = "test input"
        mock_prompt_session_class.return_value = mock_session
        
        session = SafePromptSession()
        result = session.prompt("Test message")
        
        # Should call prompt session
        mock_prompt_session_class.assert_called_once()
        assert result == "test input"


class TestCLISessionHandlers:
    """Test CLI session handler functions."""

    def test_show_profile_error_handling(self):
        """Test show_profile handles errors gracefully."""
        mock_console = Mock(spec=Console)
        
        # Mock personalization engine to raise an error
        with patch('app.cli.session.personalization_engine') as mock_engine:
            mock_engine.get_user_profile.side_effect = Exception("Test error")
            
            # Should not raise an exception
            show_profile("test_user", mock_console)
            
            # Should show error message
            mock_console.print.assert_called_once()
            call_args = mock_console.print.call_args[0][0]
            assert "Could not load profile" in call_args

    def test_show_patterns_error_handling(self):
        """Test show_patterns handles errors gracefully."""
        mock_console = Mock(spec=Console)
        
        # Mock pattern detector to raise an error
        with patch('app.cli.session.pattern_detector') as mock_detector:
            mock_detector.get_temporal_patterns.side_effect = Exception("Test error")
            
            # Should not raise an exception
            show_patterns("test_user", mock_console)
            
            # Should show error message
            mock_console.print.assert_called_once()
            call_args = mock_console.print.call_args[0][0]
            assert "Could not load patterns" in call_args

    def test_show_history_error_handling(self):
        """Test show_history handles errors gracefully."""
        mock_console = Mock(spec=Console)
        
        # Mock memory manager to raise an error
        with patch('app.cli.session.memory_manager') as mock_manager:
            mock_manager.get_user_memories.side_effect = Exception("Test error")
            
            # Should not raise an exception
            show_history("test_user", mock_console)
            
            # Should show error message
            mock_console.print.assert_called_once()
            call_args = mock_console.print.call_args[0][0]
            assert "Could not load history" in call_args

    def test_show_about_functionality(self):
        """Test show_about displays application information."""
        mock_console = Mock(spec=Console)
        
        # Should not raise an exception
        show_about(mock_console)
        
        # Should display about information
        mock_console.print.assert_called_once()

    def test_show_settings_functionality(self):
        """Test show_settings displays application settings."""
        mock_console = Mock(spec=Console)
        
        # Should not raise an exception
        show_settings(mock_console)
        
        # Should display settings information
        mock_console.print.assert_called_once()

    def test_handle_model_switch_show_available(self):
        """Test handle_model_switch shows available models when no args."""
        mock_console = Mock(spec=Console)
        
        # Should show available models
        team, system_name = handle_model_switch("", mock_console)
        
        # Should display model information
        mock_console.print.assert_called_once()

    @patch('app.cli.session.create_migru_agent')
    def test_handle_model_switch_valid_model(self, mock_create_agent):
        """Test handle_model_switch handles valid model switching."""
        mock_console = Mock(spec=Console)
        mock_agent = Mock()
        mock_agent.model = "test-model"
        mock_create_agent.return_value = mock_agent
        
        # Should switch to new model
        team, system_name = handle_model_switch("mistral", mock_console)
        
        # Should create new agent
        mock_create_agent.assert_called_once()
        assert team == mock_agent
        assert system_name == "Mistral AI"

    def test_handle_model_switch_invalid_model(self):
        """Test handle_model_switch handles invalid model gracefully."""
        mock_console = Mock(spec=Console)
        
        # Should handle invalid model
        with patch('app.cli.session.create_migru_agent') as mock_create_agent:
            mock_create_agent.side_effect = Exception("Test error")
            
            team, system_name = handle_model_switch("invalid-model", mock_console)
            
            # Should show error message
            mock_console.print.assert_called()
            call_args = mock_console.print.call_args[0][0]
            assert "Failed to switch model" in call_args


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_cli_handlers_graceful_degradation(self):
        """Test that CLI handlers degrade gracefully when services fail."""
        mock_console = Mock(spec=Console)
        
        # Test various handlers with mocked failures
        handlers_to_test = [
            (show_profile, "test_user"),
            (show_patterns, "test_user"),
            (show_history, "test_user"),
        ]
        
        for handler, *args in handlers_to_test:
            # Reset mock
            mock_console.reset_mock()
            
            # Mock the service to fail
            with patch('app.cli.session.personalization_engine') as mock_engine:
                mock_engine.get_user_profile.side_effect = Exception("Service unavailable")
                
                # Should not raise an exception
                handler(*args, mock_console)
                
                # Should show user-friendly error
                mock_console.print.assert_called()
                call_args = mock_console.print.call_args[0][0]
                assert "Could not load" in call_args or "Error" in call_args