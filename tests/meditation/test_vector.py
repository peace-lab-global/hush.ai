"""测试 ChromaDB 向量数据库操作。"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from hushai.meditation.config import MeditationConfig, reset_config, set_config


@pytest.fixture(autouse=True)
def _reset_config_fixture():
    yield
    reset_config()


def _setup_config_and_mock_client():
    cfg = MeditationConfig(jwt_secret="test")
    set_config(cfg)
    mock_client = MagicMock()
    return mock_client


class TestAddKnowledgeChunks:
    @patch("hushai.meditation.db.vector._get_client")
    def test_empty_list_returns_early(self, mock_get_client):
        from hushai.meditation.db.vector import add_knowledge_chunks

        mock_get_client.return_value = MagicMock()
        add_knowledge_chunks([])
        mock_get_client.assert_not_called()

    @patch("hushai.meditation.db.vector.knowledge_collection")
    def test_adds_chunks_with_metadata(self, mock_knowledge_col):
        from hushai.meditation.db.vector import add_knowledge_chunks

        _setup_config_and_mock_client()
        mock_col = MagicMock()
        mock_knowledge_col.return_value = mock_col

        chunks = [
            {
                "id": "c1",
                "content": "正念呼吸内容",
                "title": "正念入门",
                "tags": ["冥想", "入门"],
                "source": "book1",
                "parent_id": "p1",
            },
            {
                "id": "c2",
                "content": "身体扫描内容",
                "title": "身体扫描",
                "tags": [],
                "source": None,
                "parent_id": None,
            },
        ]
        add_knowledge_chunks(chunks)

        mock_col.upsert.assert_called_once()
        call_kwargs = mock_col.upsert.call_args
        assert call_kwargs.kwargs["ids"] == ["c1", "c2"]
        assert call_kwargs.kwargs["documents"] == ["正念呼吸内容", "身体扫描内容"]
        metas = call_kwargs.kwargs["metadatas"]
        assert metas[0]["title"] == "正念入门"
        assert metas[0]["tags"] == "冥想,入门"
        assert metas[0]["source"] == "book1"
        assert metas[0]["parent_id"] == "p1"
        assert "tags" not in metas[1] or metas[1].get("tags") is None or metas[1] == {}


class TestSearchKnowledge:
    @patch("hushai.meditation.db.vector.knowledge_collection")
    def test_empty_collection_returns_empty(self, mock_knowledge_col):
        from hushai.meditation.db.vector import search_knowledge

        mock_col = MagicMock()
        mock_col.count.return_value = 0
        mock_knowledge_col.return_value = mock_col

        result = search_knowledge("冥想")
        assert result == []

    @patch("hushai.meditation.db.vector.knowledge_collection")
    def test_returns_scored_results(self, mock_knowledge_col):
        from hushai.meditation.db.vector import search_knowledge

        mock_col = MagicMock()
        mock_col.count.return_value = 2
        mock_col.query.return_value = {
            "ids": [["k1", "k2"]],
            "documents": [["正念内容", "呼吸内容"]],
            "distances": [[0.1, 0.3]],
            "metadatas": [
                [
                    {"title": "正念入门", "tags": "冥想,入门"},
                    {"title": "呼吸法"},
                ]
            ],
        }
        mock_knowledge_col.return_value = mock_col

        result = search_knowledge("正念")
        assert len(result) == 2
        assert result[0]["id"] == "k1"
        assert result[0]["score"] == pytest.approx(0.9)
        assert result[0]["title"] == "正念入门"
        assert result[0]["tags"] == ["冥想", "入门"]
        assert result[1]["id"] == "k2"
        assert result[1]["score"] == pytest.approx(0.7)

    @patch("hushai.meditation.db.vector.knowledge_collection")
    def test_empty_ids_returns_empty(self, mock_knowledge_col):
        from hushai.meditation.db.vector import search_knowledge

        mock_col = MagicMock()
        mock_col.count.return_value = 5
        mock_col.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "distances": [[]],
            "metadatas": [[]],
        }
        mock_knowledge_col.return_value = mock_col

        result = search_knowledge("空")
        assert result == []


class TestAddMemoryEmbedding:
    @patch("hushai.meditation.db.vector.memory_collection")
    def test_calls_upsert_correctly(self, mock_memory_col):
        from hushai.meditation.db.vector import add_memory_embedding

        mock_col = MagicMock()
        mock_memory_col.return_value = mock_col

        add_memory_embedding("m1", "用户每天冥想15分钟", "u1", "meditation_experience")

        mock_col.upsert.assert_called_once_with(
            ids=["m1"],
            documents=["用户每天冥想15分钟"],
            metadatas=[{"user_id": "u1", "category": "meditation_experience"}],
        )


class TestSearchMemories:
    @patch("hushai.meditation.db.vector.memory_collection")
    def test_empty_collection_returns_empty(self, mock_memory_col):
        from hushai.meditation.db.vector import search_memories

        mock_col = MagicMock()
        mock_col.count.return_value = 0
        mock_memory_col.return_value = mock_col

        result = search_memories("冥想", "u1")
        assert result == []

    @patch("hushai.meditation.db.vector.memory_collection")
    def test_returns_memories_with_category(self, mock_memory_col):
        from hushai.meditation.db.vector import search_memories

        mock_col = MagicMock()
        mock_col.count.return_value = 1
        mock_col.query.return_value = {
            "ids": [["m1"]],
            "documents": [["每天冥想15分钟"]],
            "distances": [[0.2]],
            "metadatas": [[{"category": "meditation_experience", "user_id": "u1"}]],
        }
        mock_memory_col.return_value = mock_col

        result = search_memories("冥想习惯", "u1")
        assert len(result) == 1
        assert result[0]["id"] == "m1"
        assert result[0]["score"] == pytest.approx(0.8)
        assert result[0]["category"] == "meditation_experience"


class TestDeleteMemoryEmbedding:
    @patch("hushai.meditation.db.vector.memory_collection")
    def test_calls_delete(self, mock_memory_col):
        from hushai.meditation.db.vector import delete_memory_embedding

        mock_col = MagicMock()
        mock_memory_col.return_value = mock_col

        delete_memory_embedding("m1")

        mock_col.delete.assert_called_once_with(ids=["m1"])
