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
        app_name="Alora",
        user_id="test_user",
    )

    # Assert that run_live was called
    mock_runner.run_live.assert_called_once()

@patch("main.vertexai.init")
@patch("main.Connector", new_callable=MagicMock)
@patch("main.DatabaseSessionService", new_callable=MagicMock)
def test_initialize_services_with_database(
    mock_db_session_service, mock_connector, mock_vertexai_init, monkeypatch
):
    """Test that initialize_services initializes the database correctly."""
    # Set environment variables for the database connection
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASS", "test_pass")
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("INSTANCE_CONNECTION_NAME", "test_instance")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test_project")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "test_location")

    # Call the function
    from main import initialize_services
    initialize_services()

    # Assert that the DatabaseSessionService was initialized with the correct arguments
    call_args = mock_db_session_service.call_args
    assert call_args[1]["db_url"] == "postgresql+pg8000://"
    assert callable(call_args[1]["creator"])