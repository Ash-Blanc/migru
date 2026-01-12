"""Unit tests for memory module."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from app.memory import SafeMemoryManager, SafeCultureManager
from agno.memory import MemoryManager
from agno.db.base import BaseDb


class TestSafeMemoryManager:
    """Test SafeMemoryManager functionality."""

    def setup_method(self):
        """Setup test database mock."""
        self.mock_db = Mock(spec=BaseDb)
        self.user_id = "test_user"
        self.memory_manager = SafeMemoryManager(self.mock_db)

    def test_parse_topics_with_list(self):
        """Test parse_topics with list input."""
        topics = ["topic1", "topic2"]
        result = self.memory_manager._parse_topics(topics)
        assert result == topics

    def test_parse_topics_with_string_list(self):
        """Test parse_topics with stringified list."""
        topics = "['topic1', 'topic2']"
        result = self.memory_manager._parse_topics(topics)
        assert result == ["topic1", "topic2"]

    def test_parse_topics_with_single_string(self):
        """Test parse_topics with single string."""
        topics = "single_topic"
        result = self.memory_manager._parse_topics(topics)
        assert result == ["single_topic"]

    def test_parse_topics_with_none(self):
        """Test parse_topics with None input."""
        topics = None
        result = self.memory_manager._parse_topics(topics)
        assert result is None

    @patch('app.memory.uuid4')
    def test_add_memory_success(self, mock_uuid):
        """Test successful memory addition."""
        mock_uuid.return_value = Mock(hex="test-uuid")
        self.mock_db.upsert_user_memory.return_value = None

        result = self.memory_manager.add_memory(
            self.user_id,
            "test memory",
            topics=["topic1"]
        )

        assert "successfully" in result
        self.mock_db.upsert_user_memory.assert_called_once()

    def test_add_memory_failure(self):
        """Test memory addition failure."""
        self.mock_db.upsert_user_memory.side_effect = Exception("DB error")

        result = self.memory_manager.add_memory(
            self.user_id,
            "test memory"
        )

        assert "Error" in result

    def test_update_memory_success(self):
        """Test successful memory update."""
        self.mock_db.upsert_user_memory.return_value = None

        result = self.memory_manager.update_memory(
            self.user_id,
            "test-uuid",
            "updated memory"
        )

        assert "successfully" in result

    def test_delete_memory_success(self):
        """Test successful memory deletion."""
        self.mock_db.delete_user_memory.return_value = None

        result = self.memory_manager.delete_memory(
            self.user_id,
            "test-uuid"
        )

        assert "successfully" in result

    def test_clear_memory(self):
        """Test memory clearing."""
        self.mock_db.clear_memories.return_value = None

        result = self.memory_manager.clear_memory(self.user_id)

        assert "successfully" in result
        self.mock_db.clear_memories.assert_called_once()


class TestSafeCultureManager:
    """Test SafeCultureManager functionality."""

    def setup_method(self):
        """Setup test database mock."""
        self.mock_db = Mock(spec=BaseDb)
        self.culture_manager = SafeCultureManager(self.mock_db)

    def test_parse_list_with_list(self):
        """Test parse_list with list input."""
        items = ["item1", "item2"]
        result = self.culture_manager._parse_list(items)
        assert result == items

    def test_parse_list_with_string_list(self):
        """Test parse_list with stringified list."""
        items = "['item1', 'item2']"
        result = self.culture_manager._parse_list(items)
        assert result == ["item1", "item2"]

    def test_parse_list_with_single_string(self):
        """Test parse_list with single string."""
        items = "single_item"
        result = self.culture_manager._parse_list(items)
        assert result == ["single_item"]

    def test_parse_list_with_none(self):
        """Test parse_list with None input."""
        items = None
        result = self.culture_manager._parse_list(items)
        assert result is None

    @patch('app.memory.uuid4')
    def test_add_cultural_knowledge_success(self, mock_uuid):
        """Test successful cultural knowledge addition."""
        mock_uuid.return_value = Mock(hex="test-uuid")
        self.mock_db.upsert_cultural_knowledge.return_value = None

        result = self.culture_manager.add_cultural_knowledge(
            name="test knowledge",
            summary="test summary",
            content="test content",
            categories=["category1"]
        )

        assert "successfully" in result
        self.mock_db.upsert_cultural_knowledge.assert_called_once()

    def test_add_cultural_knowledge_failure(self):
        """Test cultural knowledge addition failure."""
        self.mock_db.upsert_cultural_knowledge.side_effect = Exception("DB error")

        result = self.culture_manager.add_cultural_knowledge(
            name="test knowledge"
        )

        assert "Error" in result