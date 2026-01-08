
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import json
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

    with client.websocket_connect("/ws/123?is_audio=false", headers={"Sec-WebSocket-Protocol": "Bearer, test-token"}) as websocket:
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
        app_name="agents",
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

@patch("main.audio_service")
def test_synthesize_endpoint(mock_audio_service):
    """Test the /synthesize endpoint."""
    mock_audio_service.generate_and_upload.return_value = "https://fake.url/audio.mp3"
    
    response = client.post("/synthesize", json={"text": "Hello"})
    
    assert response.status_code == 200
    assert response.json() == {"audio_url": "https://fake.url/audio.mp3"}
    mock_audio_service.generate_and_upload.assert_called_once_with("Hello", "JBFqnCBsd6RMkjVDRZzb")

@pytest.mark.asyncio
async def test_analyze_endpoint(mocker):
    """Test the /analyze endpoint with streaming response."""
    # Mock the global runner
    mock_runner = MagicMock()
    mocker.patch("main.runner", mock_runner)
    
    # Mock run_async to yield an event
    from google.adk.events import Event
    from google.genai.types import Content, Part
    
    async def mock_run_gen(*args, **kwargs):
        # Yield a text part
        yield Event(
            source="agent", 
            content=Content(parts=[Part(text="Analysis result")])
        )
    mock_runner.run_async.side_effect = mock_run_gen
    
    # Needs session service to create temp session
    mock_runner.session_service.create_session = AsyncMock(return_value=MagicMock())

    with client.stream("POST", "/analyze", json={"query": "test query"}) as response:
        assert response.status_code == 200
        # Consume the stream
        lines = list(response.iter_lines())
        
        # We expect NDJSON lines. 
        # The logic in main.py puts ("TEXT", "Analysis result") into output queue
        # Then the streaming loop consumes it and yields {"result": {"text": ...}} eventually
        # Or intermediate parts?
        # Let's check main.py logic:
        # It aggregates TEXT types.
        # It waits for DONE.
        
    # Since our mock generator ends, the 'finally' block in agent_producer sends DONE.
    # The consumer loop should see DONE and yield the result.
    
    # Verify we got some JSON
    assert len(lines) > 0
    last_line = json.loads(lines[-1])
    # The analyze endpoint aggregates text and returns a "result" object at the end
    assert "result" in last_line or "log" in last_line