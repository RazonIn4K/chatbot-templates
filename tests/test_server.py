"""
Tests for the FastAPI server endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from server import app
from llm_client import LLMClient, LLMClientError


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    mock_client = Mock(spec=LLMClient)
    mock_client.provider = "openai"
    mock_client.model = "gpt-3.5-turbo"
    mock_client.generate.return_value = "This is a test response from the LLM."
    return mock_client


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_returns_200(self, client):
        """Test that the root endpoint returns 200 OK."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_contains_version(self, client):
        """Test that the root endpoint contains version information."""
        response = client.get("/")
        data = response.json()
        assert "version" in data
        assert data["version"] == "2.0.0"

    def test_root_lists_endpoints(self, client):
        """Test that the root endpoint lists available endpoints."""
        response = client.get("/")
        data = response.json()
        assert "endpoints" in data
        assert "/chat" in data["endpoints"]
        assert "/chat-with-retrieval" in data["endpoints"]


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    @patch('server.get_llm_client')
    def test_health_check_healthy(self, mock_get_client, client, mock_llm_client):
        """Test health check when LLM client is working."""
        mock_get_client.return_value = mock_llm_client
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "llm_provider" in data
        assert "llm_model" in data

    @patch('server.get_llm_client')
    def test_health_check_unhealthy(self, mock_get_client, client):
        """Test health check when LLM client fails."""
        mock_get_client.side_effect = Exception("API key not configured")
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "error" in data


class TestChatEndpoint:
    """Tests for the /chat endpoint."""

    @patch('server.get_llm_client')
    def test_chat_returns_200(self, mock_get_client, client, mock_llm_client):
        """Test that /chat returns 200 with valid input."""
        mock_get_client.return_value = mock_llm_client

        response = client.post(
            "/chat",
            json={"message": "Hello, how are you?"}
        )
        assert response.status_code == 200

    @patch('server.get_llm_client')
    def test_chat_returns_non_empty_response(self, mock_get_client, client, mock_llm_client):
        """Test that /chat returns a non-empty response."""
        mock_get_client.return_value = mock_llm_client

        response = client.post(
            "/chat",
            json={"message": "What is FastAPI?"}
        )
        data = response.json()
        assert "response" in data
        assert len(data["response"]) > 0
        assert data["response"] == "This is a test response from the LLM."

    @patch('server.get_llm_client')
    def test_chat_includes_system_prompt(self, mock_get_client, client, mock_llm_client):
        """Test that /chat includes the system prompt in response."""
        mock_get_client.return_value = mock_llm_client

        response = client.post(
            "/chat",
            json={"message": "Test message"}
        )
        data = response.json()
        assert "system_prompt" in data
        assert len(data["system_prompt"]) > 0

    @patch('server.get_llm_client')
    def test_chat_with_context(self, mock_get_client, client, mock_llm_client):
        """Test /chat with context provided."""
        mock_get_client.return_value = mock_llm_client

        response = client.post(
            "/chat",
            json={
                "message": "What is the capital?",
                "context": "France is a country in Europe. Its capital is Paris."
            }
        )
        data = response.json()
        assert response.status_code == 200
        assert data["context_used"] is True

        # Verify that generate was called with context
        mock_llm_client.generate.assert_called_once()
        call_args = mock_llm_client.generate.call_args
        assert call_args[1]["context"] == "France is a country in Europe. Its capital is Paris."

    @patch('server.get_llm_client')
    def test_chat_without_context(self, mock_get_client, client, mock_llm_client):
        """Test /chat without context."""
        mock_get_client.return_value = mock_llm_client

        response = client.post(
            "/chat",
            json={"message": "Hello"}
        )
        data = response.json()
        assert response.status_code == 200
        assert data["context_used"] is False

    def test_chat_empty_message_returns_400(self, client):
        """Test that /chat returns 400 for empty message."""
        response = client.post(
            "/chat",
            json={"message": ""}
        )
        assert response.status_code == 400

    def test_chat_missing_message_returns_422(self, client):
        """Test that /chat returns 422 for missing message field."""
        response = client.post(
            "/chat",
            json={}
        )
        assert response.status_code == 422

    @patch('server.get_llm_client')
    def test_chat_llm_error_returns_500(self, mock_get_client, client):
        """Test that /chat returns 500 when LLM client fails."""
        mock_client = Mock(spec=LLMClient)
        mock_client.generate.side_effect = LLMClientError("API error")
        mock_get_client.return_value = mock_client

        response = client.post(
            "/chat",
            json={"message": "Test message"}
        )
        assert response.status_code == 500
        assert "Failed to generate response" in response.json()["detail"]


class TestChatWithRetrievalEndpoint:
    """Tests for the /chat-with-retrieval endpoint."""

    @patch('server.retrieve_relevant_context')
    @patch('server.get_llm_client')
    def test_chat_with_retrieval_returns_200(
        self, mock_get_client, mock_retrieve, client, mock_llm_client
    ):
        """Test that /chat-with-retrieval returns 200."""
        mock_get_client.return_value = mock_llm_client
        mock_retrieve.return_value = "Retrieved context from vector DB"

        response = client.post(
            "/chat-with-retrieval",
            json={"message": "What is RAG?"}
        )
        assert response.status_code == 200

    @patch('server.retrieve_relevant_context')
    @patch('server.get_llm_client')
    def test_chat_with_retrieval_calls_retriever(
        self, mock_get_client, mock_retrieve, client, mock_llm_client
    ):
        """Test that /chat-with-retrieval calls the retriever."""
        mock_get_client.return_value = mock_llm_client
        mock_retrieve.return_value = "Retrieved context"

        response = client.post(
            "/chat-with-retrieval",
            json={"message": "What is RAG?"}
        )

        # Verify retriever was called with the query
        mock_retrieve.assert_called_once()
        call_args = mock_retrieve.call_args
        assert call_args[1]["query"] == "What is RAG?"

    @patch('server.retrieve_relevant_context')
    @patch('server.get_llm_client')
    def test_chat_with_retrieval_uses_retrieved_context(
        self, mock_get_client, mock_retrieve, client, mock_llm_client
    ):
        """Test that retrieved context is passed to LLM."""
        mock_get_client.return_value = mock_llm_client
        retrieved_context = "RAG stands for Retrieval-Augmented Generation"
        mock_retrieve.return_value = retrieved_context

        response = client.post(
            "/chat-with-retrieval",
            json={"message": "What is RAG?"}
        )

        data = response.json()
        assert response.status_code == 200
        assert data["context_used"] is True

        # Verify that generate was called with retrieved context
        mock_llm_client.generate.assert_called_once()
        call_args = mock_llm_client.generate.call_args
        assert call_args[1]["context"] == retrieved_context

    @patch('server.retrieve_relevant_context')
    @patch('server.get_llm_client')
    def test_chat_with_retrieval_empty_message_returns_400(
        self, mock_get_client, mock_retrieve, client
    ):
        """Test that /chat-with-retrieval returns 400 for empty message."""
        response = client.post(
            "/chat-with-retrieval",
            json={"message": ""}
        )
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
