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
@patch("main.initialize_services")
async def test_start_agent_session_with_memory(mock_initialize_services, mocker):
    """Test that start_agent_session uses the global runner to create a session and run it."""
    # Mock the global runner object
    mock_runner = MagicMock()
    mock_runner.session_service.create_session = AsyncMock()
    mocker.patch("main.runner", mock_runner)

    # Call the function
    await start_agent_session("test_user")

    # Assert that create_session was called with the correct arguments
    mock_runner.session_service.create_session.assert_called_with(
        app_name="ADK Streaming example",
        user_id="test_user",
    )

    # Assert that run_live was called
    mock_runner.run_live.assert_called_once()