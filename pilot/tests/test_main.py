
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from main import app, start_agent_session, initialize_services

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers['content-type']

@pytest.mark.asyncio
async def test_websocket_endpoint(mocker):
    # Mock the auth verification to bypass real Firebase initialization in tests
    mocker.patch("main.auth.verify_id_token", return_value={"uid": "test-uid"})

    live_events_mock = MagicMock()
    live_request_queue_mock = MagicMock()
    mocker.patch("main.start_agent_session", return_value=(live_events_mock, live_request_queue_mock))
    mocker.patch("main.agent_to_client_messaging")
    mocker.patch("main.client_to_agent_messaging")

    with client.websocket_connect(
        "/ws/123?is_audio=false",
        headers={"Authorization": "Bearer test-token"},
    ) as websocket:
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

@pytest.mark.asyncio
@patch("main.vertexai.init")
@patch("main.get_mongo_session_service", new_callable=AsyncMock)
@patch("main.firebase_admin.initialize_app")
@patch("main.VertexAiMemoryBankService")
@patch("main.Runner")
async def test_initialize_services(
    mock_runner,
    mock_memory_service,
    mock_firebase_app,
    mock_get_mongo_session,
    mock_vertexai_init,
    monkeypatch,
):
    """Test that initialize_services initializes all services correctly."""
    # Set environment variables
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test_project")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "test_location")
    monkeypatch.setenv("AGENT_ENGINE_ID", "test_engine_id")
    # Call the function
    runner = await initialize_services()

    # Assert that the services were initialized
    mock_vertexai_init.assert_called_once_with(project="test_project", location="test_location")
    mock_firebase_app.assert_called_once()
    mock_get_mongo_session.assert_awaited_once()
    mock_memory_service.assert_called_once_with(
        project="test_project",
        location="test_location",
        agent_engine_id="test_engine_id",
    )
    mock_runner.assert_called_once()
    assert runner == mock_runner.return_value