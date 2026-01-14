"""
Tests for Local LLM Integration and Privacy Features
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from app.models.local_llm import LocalLlamaModel, LocalModelManager, model_manager
from app.agents.smart_router import SmartRouter, TaskType
from app.core import MigruCore, PrivacyMode
from app.config_enhanced import config
from app.tools.privacy_tools import PrivacyAwareSearchTools


class TestLocalLlamaModel:
    """Test local LLM model integration."""

    @pytest.fixture
    def model(self):
        """Create a test local model."""
        return LocalLlamaModel(
            model="function-gemma:7b",
            host="http://localhost:8080",
            temperature=0.3,
            max_tokens=1024,
        )

    def test_model_initialization(self, model):
        """Test model initialization."""
        assert model.id == "function-gemma:7b"
        assert model.host == "http://localhost:8080"
        assert model.temperature == 0.3
        assert model.max_tokens == 1024
        assert model.supports_tools == True
        assert model.is_local == True

    def test_model_info(self, model):
        """Test model information retrieval."""
        info = model.get_model_info()

        assert info["model"] == "function-gemma:7b"
        assert info["host"] == "http://localhost:8080"
        assert info["supports_tools"] == True
        assert info["is_local"] == True
        assert info["temperature"] == 0.3
        assert info["max_tokens"] == 1024

    def test_optimize_for_conversation_type(self, model):
        """Test conversation type optimization."""
        # Test emotional support optimization
        model._optimize_for_conversation_type("emotional_support")
        assert model.temperature == 0.8
        assert model.max_tokens == 512

        # Test research optimization
        model._optimize_for_conversation_type("research")
        assert model.temperature == 0.3
        assert model.max_tokens == 1536

        # Test tool calling optimization
        model._optimize_for_conversation_type("tool_calling")
        assert model.temperature == 0.1
        assert model.max_tokens == 1024

    @pytest.mark.asyncio
    async def test_connection_success(self, model):
        """Test successful connection."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            result = await model.test_connection()
            assert result == True

    @pytest.mark.asyncio
    async def test_connection_failure(self, model):
        """Test connection failure."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = Exception("Connection failed")

            result = await model.test_connection()
            assert result == False


class TestLocalModelManager:
    """Test local model manager."""

    @pytest.fixture
    def manager(self):
        """Create a model manager."""
        return LocalModelManager()

    def test_manager_initialization(self, manager):
        """Test manager initialization."""
        assert len(manager.model_configs) > 0
        assert "function-gemma:7b" in manager.model_configs
        assert "qwen2.5:3b" in manager.model_configs

    def test_get_optimal_model(self, manager):
        """Test optimal model selection."""
        # Test routing task
        model = manager.get_optimal_model("routing")
        assert model == "function-gemma:7b"

        # Test emotional support task
        model = manager.get_optimal_model("emotional_support")
        assert model == "qwen2.5:3b"

        # Test research task
        model = manager.get_optimal_model("research")
        assert model == "function-gemma:7b"

    def test_create_model_for_task(self, manager):
        """Test model creation for specific tasks."""
        model = manager.create_model_for_task("emotional_support")

        assert isinstance(model, LocalLlamaModel)
        assert model.temperature == 0.8  # Optimized for empathy
        assert model.max_tokens == 512

    @pytest.mark.asyncio
    async def test_scan_available_models_success(self, manager):
        """Test successful model scanning."""
        with patch("httpx.AsyncClient.get") as mock_get:
            # Mock Ollama response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [{"name": "qwen2.5:3b"}, {"name": "function-gemma:7b"}]
            }
            mock_get.return_value = mock_response

            models = await manager.scan_available_models()

            assert len(models) >= 2
            assert "qwen2.5:3b" in models
            assert "function-gemma:7b" in models

    @pytest.mark.asyncio
    async def test_scan_available_models_failure(self, manager):
        """Test model scanning failure."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = Exception("Scan failed")

            models = await manager.scan_available_models()
            assert len(models) == 0


class TestSmartRouter:
    """Test smart router functionality."""

    @pytest.fixture
    def router(self):
        """Create a smart router."""
        return SmartRouter()

    def test_analyze_task_emotional_support(self, router):
        """Test emotional support task analysis."""
        message = "I'm feeling really anxious and overwhelmed"
        task_type = router.analyze_task(message)

        assert task_type == TaskType.EMOTIONAL_SUPPORT

    def test_analyze_task_research(self, router):
        """Test research task analysis."""
        message = "Search for latest studies on migraine treatments"
        task_type = router.analyze_task(message)

        assert task_type == TaskType.RESEARCH

    def test_analyze_task_practical_advice(self, router):
        """Test practical advice task analysis."""
        message = "How should I create a daily routine for stress management?"
        task_type = router.analyze_task(message)

        assert task_type == TaskType.PRACTICAL_ADVICE

    def test_analyze_task_tool_execution(self, router):
        """Test tool execution task analysis."""
        message = "Search for weather information and analyze the data"
        task_type = router.analyze_task(message)

        assert task_type == TaskType.TOOL_EXECUTION

    def test_analyze_task_general_conversation(self, router):
        """Test general conversation task analysis."""
        message = "Hello, how are you today?"
        task_type = router.analyze_task(message)

        assert task_type == TaskType.GENERAL_CONVERSATION

    def test_analyze_task_with_context(self, router):
        """Test task analysis with context."""
        message = "I'm having a tough day"
        context = {"user_mood": "anxious"}

        task_type = router.analyze_task(message, context)

        # Should prioritize emotional support with anxious mood
        assert task_type == TaskType.EMOTIONAL_SUPPORT

    @pytest.mark.asyncio
    async def test_route_to_agent(self, router):
        """Test agent routing."""
        message = "I need help with my anxiety"

        with patch.object(router, "_get_or_create_agent") as mock_get_agent:
            mock_agent = Mock()
            mock_get_agent.return_value = mock_agent

            agent, reason = await router.route_to_agent(message)

            assert agent == mock_agent
            assert "Task type: emotional_support" in reason
            assert "Model:" in reason

    def test_get_routing_stats_empty(self, router):
        """Test routing stats with no history."""
        stats = router.get_routing_stats()

        assert stats["total_routes"] == 0
        assert "task_distribution" in stats
        assert "model_distribution" in stats

    def test_get_routing_stats_with_history(self, router):
        """Test routing stats with history."""
        router.task_history = [
            {"task_type": "emotional_support", "model": "qwen2.5:3b"},
            {"task_type": "research", "model": "function-gemma:7b"},
            {"task_type": "emotional_support", "model": "qwen2.5:3b"},
        ]

        stats = router.get_routing_stats()

        assert stats["total_routes"] == 3
        assert stats["task_distribution"]["emotional_support"] == 2
        assert stats["task_distribution"]["research"] == 1


class TestMigruCore:
    """Test enhanced Migru core."""

    @pytest.fixture
    def core(self):
        """Create a Migru core instance."""
        return MigruCore()

    @pytest.mark.asyncio
    async def test_core_initialization(self, core):
        """Test core initialization."""
        with patch.object(model_manager, "scan_available_models") as mock_scan:
            with patch.object(core.router, "initialize") as mock_init:
                mock_scan.return_value = []
                mock_init.return_value = None

                await core.initialize()

                mock_scan.assert_called_once()
                mock_init.assert_called_once()

    def test_switch_privacy_mode_success(self, core):
        """Test successful privacy mode switch."""
        result = core.switch_privacy_mode("local")

        assert result == True
        assert core.privacy_mode == "local"

    def test_switch_privacy_mode_failure(self, core):
        """Test failed privacy mode switch."""
        result = core.switch_privacy_mode("invalid")

        assert result == False
        assert core.privacy_mode != "invalid"

    def test_get_system_status(self, core):
        """Test system status retrieval."""
        status = core.get_system_status()

        assert "privacy_mode" in status
        assert "local_llm_enabled" in status
        assert "available_models" in status
        assert "active_agents" in status
        assert "routing_stats" in status
        assert "performance" in status


class TestPrivacyAwareSearchTools:
    """Test privacy-aware search tools."""

    @pytest.fixture
    def tools(self):
        """Create privacy-aware search tools."""
        return PrivacyAwareSearchTools("hybrid")

    def test_search_allowed_hybrid(self, tools):
        """Test search allowed in hybrid mode."""
        tools.privacy_mode = "hybrid"
        with patch.dict(config.__dict__, {"ENABLE_SEARCH_IN_LOCAL_MODE": True}):
            assert tools._is_search_allowed() == True

    def test_search_disallowed_local(self, tools):
        """Test search disallowed in local mode."""
        tools.privacy_mode = "local"
        assert tools._is_search_allowed() == False

    def test_search_allowed_flexible(self, tools):
        """Test search allowed in flexible mode."""
        tools.privacy_mode = "flexible"
        assert tools._is_search_allowed() == True

    def test_privacy_notice_search(self, tools):
        """Test privacy notice for search."""
        tools.privacy_mode = "local"
        notice = tools._get_privacy_notice("search")

        assert "🔒 **Privacy Mode Active**" in notice
        assert "Search is currently disabled" in notice

    def test_check_search_permissions(self, tools):
        """Test search permissions check."""
        result = tools.check_search_permissions()

        # Should be valid JSON
        import json

        permissions = json.loads(result)

        assert "privacy_mode" in permissions
        assert "search_enabled" in permissions
        assert "search_sources" in permissions
        assert "recommendations" in permissions


class TestConfigEnhanced:
    """Test enhanced configuration."""

    def test_current_model_config_local(self, config):
        """Test current model config for local models."""
        config.LOCAL_LLM_ENABLED = True
        config.LOCAL_LLM_MODEL = "function-gemma:7b"
        config.LOCAL_LLM_HOST = "http://localhost:8080"

        model_config = config.current_model_config

        assert model_config["type"] == "local"
        assert model_config["model"] == "function-gemma:7b"
        assert model_config["host"] == "http://localhost:8080"

    def test_search_enabled_local_mode(self, config):
        """Test search enabled in local mode."""
        config.PRIVACY_MODE = "local"
        assert config.search_enabled == False

    def test_search_enabled_hybrid_mode(self, config):
        """Test search enabled in hybrid mode."""
        config.PRIVACY_MODE = "hybrid"
        config.ENABLE_SEARCH_IN_LOCAL_MODE = True
        assert config.search_enabled == True

    def test_search_enabled_flexible_mode(self, config):
        """Test search enabled in flexible mode."""
        config.PRIVACY_MODE = "flexible"
        assert config.search_enabled == True

    def test_get_local_host(self, config):
        """Test getting appropriate local host."""
        config.LOCAL_SERVER_TYPE = "ollama"
        config.OLLAMA_HOST = "http://localhost:11434"

        host = config.get_local_host()
        assert host == "http://localhost:11434"

    def test_update_privacy_mode(self, config):
        """Test updating privacy mode."""
        result = config.update_privacy_mode("local")

        assert result == True
        assert config.PRIVACY_MODE == "local"
        assert os.environ["PRIVACY_MODE"] == "local"

    def test_get_model_recommendations(self, config):
        """Test model recommendations."""
        recommendations = config.get_model_recommendations()

        assert "local_models" in recommendations
        assert "cloud_fallbacks" in recommendations
        assert "privacy_recommendations" in recommendations

        # Check specific models
        assert "function-gemma:7b" in recommendations["local_models"]
        assert "qwen2.5:3b" in recommendations["local_models"]


# Integration Tests
class TestIntegration:
    """Integration tests for the complete system."""

    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test the full pipeline from message to response."""
        # This would test the complete integration
        # but requires actual local models to be running
        pass

    @pytest.mark.asyncio
    async def test_privacy_mode_switching(self):
        """Test privacy mode switching during runtime."""
        core = MigruCore()

        # Start in hybrid mode
        core.privacy_mode = "hybrid"
        assert core.privacy_mode == "hybrid"

        # Switch to local mode
        success = core.switch_privacy_mode("local")
        assert success == True
        assert core.privacy_mode == "local"

        # Switch to flexible mode
        success = core.switch_privacy_mode("flexible")
        assert success == True
        assert core.privacy_mode == "flexible"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
