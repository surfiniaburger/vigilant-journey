from fastapi.testclient import TestClient
from unittest.mock import patch
from server import mcp

# The MCP server exposes a FastAPI app at the .app attribute
client = TestClient(mcp.app)

def test_ask_amg_manual_success():
    """Tests the happy path where the RAG pipeline succeeds."""
    # Mock the internal functions to avoid real AI/DB calls
    with patch('server.search_manual') as mock_search,
         patch('server.generate_answer') as mock_generate:
        
        # Define what our mocks should return
        mock_search.return_value = "This is the context from the manual."
        mock_generate.return_value = "This is the final generated answer."

        # Make a request to the test client
        response = client.post(
            "/ask_amg_manual",
            json={"question": "How do I use RACE START?"}
        )

        # Assert the response is what we expect
        assert response.status_code == 200
        assert response.json() == {"answer": "This is the final generated answer."}

        # Assert our mocks were called correctly
        mock_search.assert_called_once_with("How do I use RACE START?")
        mock_generate.assert_called_once_with("How do I use RACE START?", "This is the context from the manual.")

def test_ask_amg_manual_pipeline_error():
    """Tests the case where the RAG pipeline fails."""
    # Mock the search function to raise an exception
    with patch('server.search_manual') as mock_search:
        mock_search.side_effect = Exception("Elasticsearch connection failed")

        # Make a request to the test client
        response = client.post(
            "/ask_amg_manual",
            json={"question": "A question that will cause an error"}
        )

        # Assert that the server handled the error gracefully
        assert response.status_code == 200
        assert "error" in response.json()
        assert "I encountered an issue" in response.json()["error"]
