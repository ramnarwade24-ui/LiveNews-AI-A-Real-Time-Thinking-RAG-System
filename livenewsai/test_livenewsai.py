"""
Test suite for LiveNewsAI.
Includes unit tests and integration tests.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Test configuration
TEST_TIMEOUT = 10


class TestConfig:
    """Test configuration module."""

    def test_config_load_from_env(self):
        """Test loading config from environment variables."""
        from livenewsai.config import Config

        config = Config()
        assert config.EMBEDDING_DIMENSION == 1536
        assert config.NEWS_POLLING_INTERVAL == 60


class TestNewsAPIConnector:
    """Test NewsAPI connector."""

    @patch("livenewsai.connectors.requests.get")
    def test_fetch_articles_success(self, mock_get):
        """Test successful article fetch."""
        from livenewsai.connectors import NewsAPIConnector

        # Mock response
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "source": {"name": "BBC"},
                    "title": "Test Article",
                    "description": "Test Description",
                    "content": "Test Content",
                    "url": "https://example.com/article1",
                    "urlToImage": None,
                    "publishedAt": "2024-01-18T10:00:00Z",
                    "author": "Test Author",
                }
            ],
        }
        mock_get.return_value = mock_response

        connector = NewsAPIConnector(api_key="test_key")
        articles = connector._fetch_articles()

        assert len(articles) == 1
        assert articles[0]["title"] == "Test Article"

    @patch("livenewsai.connectors.requests.get")
    def test_fetch_articles_api_error(self, mock_get):
        """Test handling of API errors."""
        from livenewsai.connectors import NewsAPIConnector

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "status": "error",
            "message": "API error",
        }
        mock_get.return_value = mock_response

        connector = NewsAPIConnector(api_key="test_key")
        articles = connector._fetch_articles()

        assert articles == []

    def test_parse_article_valid(self):
        """Test parsing valid article."""
        from livenewsai.connectors import NewsAPIConnector

        connector = NewsAPIConnector(api_key="test_key")

        article_dict = {
            "source": {"name": "BBC"},
            "title": "Test Article",
            "description": "Test Description",
            "content": "Test Content",
            "url": "https://example.com/article1",
            "urlToImage": None,
            "publishedAt": "2024-01-18T10:00:00Z",
            "author": "Test Author",
        }

        article = connector._parse_article(article_dict)

        assert article is not None
        assert article.title == "Test Article"
        assert article.source == "BBC"

    def test_parse_article_duplicate(self):
        """Test duplicate article detection."""
        from livenewsai.connectors import NewsAPIConnector

        connector = NewsAPIConnector(api_key="test_key")

        article_dict = {
            "source": {"name": "BBC"},
            "title": "Test Article",
            "url": "https://example.com/article1",
            "urlToImage": None,
            "publishedAt": "2024-01-18T10:00:00Z",
        }

        # First parse should succeed
        article1 = connector._parse_article(article_dict)
        assert article1 is not None

        # Second parse should return None (duplicate)
        article2 = connector._parse_article(article_dict)
        assert article2 is None


class TestEmbeddingProcessor:
    """Test embedding processor."""

    @patch("livenewsai.pathway_pipeline._get_openai_client")
    def test_get_embedding(self, mock_get_client):
        """Test getting embedding."""
        from livenewsai.pathway_pipeline import EmbeddingProcessor

        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3] * 512)]  # 1536 dims
        mock_client.embeddings.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        processor = EmbeddingProcessor()
        embedding = processor.get_embedding("test text")

        assert len(embedding) > 0
        mock_client.embeddings.create.assert_called_once()

    @patch("livenewsai.pathway_pipeline._get_openai_client")
    def test_get_embedding_cache(self, mock_get_client):
        """Test embedding caching."""
        from livenewsai.pathway_pipeline import EmbeddingProcessor

        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3] * 512)]
        mock_client.embeddings.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        processor = EmbeddingProcessor()

        # First call
        embedding1 = processor.get_embedding("test text")

        # Second call (should use cache)
        embedding2 = processor.get_embedding("test text")

        # API should only be called once
        assert mock_client.embeddings.create.call_count == 1
        assert embedding1 == embedding2

    @patch("livenewsai.pathway_pipeline._get_openai_client")
    def test_get_embedding_error(self, mock_get_client):
        """Test error handling in embedding."""
        from livenewsai.pathway_pipeline import EmbeddingProcessor
        from openai import OpenAIError

        mock_client = Mock()
        mock_client.embeddings.create.side_effect = OpenAIError("API Error")
        mock_get_client.return_value = mock_client

        processor = EmbeddingProcessor()
        embedding = processor.get_embedding("test text")

        # Should return zero vector on error
        assert len(embedding) == 1536
        assert all(e == 0.0 for e in embedding)


class TestVectorIndex:
    """Test vector index."""

    def test_add_document(self):
        """Test adding document to index."""
        from livenewsai.pathway_pipeline import VectorIndex

        index = VectorIndex(dimension=10)
        embedding = [0.1] * 10
        document = {"title": "Test", "url": "https://example.com"}

        index.add("doc1", embedding, document)

        assert index.size() == 1
        assert "doc1" in index.documents

    def test_search(self):
        """Test searching vector index."""
        from livenewsai.pathway_pipeline import VectorIndex
        import numpy as np

        index = VectorIndex(dimension=10)

        # Add documents
        index.add("doc1", [1.0, 0.0, 0.0] + [0.0] * 7, {"title": "Doc1"})
        index.add("doc2", [0.9, 0.1, 0.0] + [0.0] * 7, {"title": "Doc2"})
        index.add("doc3", [0.0, 1.0, 0.0] + [0.0] * 7, {"title": "Doc3"})

        # Search with similar query
        query = [1.0, 0.0, 0.0] + [0.0] * 7
        results = index.search(query, k=2)

        assert len(results) == 2
        assert results[0][0] == "doc1"  # Most similar

    def test_search_empty_index(self):
        """Test searching empty index."""
        from livenewsai.pathway_pipeline import VectorIndex

        index = VectorIndex(dimension=10)
        results = index.search([0.1] * 10, k=5)

        assert results == []


class TestRAGEngine:
    """Test RAG engine."""

    def test_build_context(self):
        """Test building context from documents."""
        from livenewsai.rag import RAGEngine

        engine = RAGEngine()

        documents = [
            {
                "title": "Article 1",
                "content": "Content 1",
                "source": "BBC",
                "published_at": "2024-01-18",
                "url": "https://example.com/1",
            },
            {
                "title": "Article 2",
                "content": "Content 2",
                "source": "CNN",
                "published_at": "2024-01-18",
                "url": "https://example.com/2",
            },
        ]

        context, urls = engine.build_context(documents)

        assert len(context) > 0
        assert len(urls) == 2
        assert "Article 1" in context
        assert "BBC" in context

    def test_build_context_max_length(self):
        """Test context length limiting."""
        from livenewsai.rag import RAGEngine

        engine = RAGEngine(max_context_length=100)

        documents = [
            {
                "title": "A" * 200,
                "content": "B" * 200,
                "source": "Source",
                "published_at": "2024-01-18",
                "url": "https://example.com",
            }
        ]

        context, urls = engine.build_context(documents)

        # Context should be limited
        assert len(context) <= 150  # Some margin for formatting

    @patch("livenewsai.rag._get_openai_client")
    def test_generate_answer(self, mock_get_client):
        """Test answer generation."""
        from livenewsai.rag import RAGEngine

        mock_client = Mock()
        mock_choice = Mock()
        mock_choice.message = Mock(content="Test answer")
        mock_response = Mock(choices=[mock_choice])
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        engine = RAGEngine()
        answer = engine.generate_answer(
            question="Test question",
            context="Test context",
        )

        assert answer == "Test answer"
        mock_client.chat.completions.create.assert_called_once()

    @patch("livenewsai.rag._get_openai_client")
    def test_generate_answer_empty_context(self, mock_get_client):
        """Test answer generation with empty context."""
        from livenewsai.rag import RAGEngine

        engine = RAGEngine()
        answer = engine.generate_answer(
            question="Test question",
            context="",
        )

        # Should return no context message
        assert "No relevant articles" in answer
        # API should not be called
        mock_get_client.assert_not_called()


class TestFastAPIServer:
    """Test FastAPI server endpoints."""

    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test root endpoint."""
        from fastapi.testclient import TestClient
        from livenewsai.app import app

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        assert "LiveNewsAI" in response.json()["name"]

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test health endpoint."""
        from fastapi.testclient import TestClient
        from livenewsai.app import app

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "index_size" in data

    @pytest.mark.asyncio
    async def test_stats_endpoint(self):
        """Test stats endpoint."""
        from fastapi.testclient import TestClient
        from livenewsai.app import app

        client = TestClient(app)
        response = client.get("/stats")

        assert response.status_code == 200
        data = response.json()
        assert "index_size" in data
        assert "embedding_dimension" in data

    @pytest.mark.asyncio
    async def test_ask_empty_index(self):
        """Test ask endpoint with empty index."""
        from fastapi.testclient import TestClient
        from livenewsai.app import app
        from livenewsai.pathway_pipeline import vector_index

        # Clear index
        vector_index.vectors.clear()
        vector_index.documents.clear()
        vector_index.ids.clear()

        client = TestClient(app)
        response = client.post(
            "/ask",
            json={"question": "Test question"},
        )

        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_ask_empty_question(self):
        """Test ask endpoint with empty question."""
        from fastapi.testclient import TestClient
        from livenewsai.app import app

        client = TestClient(app)
        response = client.post(
            "/ask",
            json={"question": ""},
        )

        assert response.status_code == 400


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
