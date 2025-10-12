import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from main import app, start_agent_session

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers['content-type']

@pytest.mark.asyncio
async def test_websocket_endpoint(mocker):
    live_events_mock = MagicMock()
    live_request_queue_mock = MagicMock()
    mocker.patch("main.start_agent_session", return_value=(live_events_mock, live_request_queue_mock))
    mocker.patch("main.agent_to_client_messaging")
    mocker.patch("main.client_to_agent_messaging")

    with client.websocket_connect("/ws/123?is_audio=false") as websocket:
        # If the connection is successful, the with block will execute without raising an exception.
        pass

@pytest.mark.asyncio
async def test_start_agent_session_with_memory(mocker):
    # Mock environment variables
    mocker.patch("os.environ.get", side_effect=lambda key: {
        "GOOGLE_CLOUD_PROJECT": "test-project",
        "GOOGLE_CLOUD_LOCATION": "test-location",
        "AGENT_ENGINE_ID": "test-agent-engine-id"
    }.get(key))

    # Mock services
    mock_vertex_memory_service = mocker.patch("main.VertexAiMemoryBankService")
    
    # Make the create_session mock awaitable
    mock_runner_instance = MagicMock()
    mock_runner_instance.session_service.create_session = AsyncMock()
    mock_runner = mocker.patch("main.Runner", return_value=mock_runner_instance)

    # Call the function
    await start_agent_session("test_user")

    # Assert that VertexAiMemoryBankService was called with the correct arguments
    mock_vertex_memory_service.assert_called_with(
        project="test-project",
        location="test-location",
        agent_engine_id="test-agent-engine-id"
    )

    # Assert that Runner was called with the memory_service
    mock_runner.assert_called_with(
        app_name="ADK Streaming example",
        agent=mocker.ANY,  # We don't need to check the agent instance itself
        session_service=mocker.ANY,
        memory_service=mock_vertex_memory_service.return_value
    )