import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from main import app
import json
import sys

# Mock motor module to avoid ImportError in the test environment
sys.modules['motor'] = MagicMock()
sys.modules['motor.motor_asyncio'] = MagicMock()

client = TestClient(app)

@pytest.mark.asyncio
async def test_audio_stream(mocker):
    # Mock the auth verification to bypass real Firebase initialization in tests
    mocker.patch("main.auth.verify_id_token", return_value={"uid": "test-uid"})

    # This is an async generator
    async def mock_events():
        yield MagicMock(
            content=MagicMock(
                parts=[MagicMock(
                    inline_data=MagicMock(
                        mime_type="audio/pcm",
                        data=b"fakedata"
                    ),
                    text=None,
                )]
            ),
            turn_complete=False,
            interrupted=False,
        )

    live_events_mock = mock_events()
    live_request_queue_mock = MagicMock()
    mocker.patch("main.start_agent_session", new_callable=AsyncMock, return_value=(live_events_mock, live_request_queue_mock))

    with client.websocket_connect("/ws/123?is_audio=true&token=test-token") as websocket:
        mock_audio_data = "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA="

        websocket.send_json({
            "mime_type": "audio/pcm",
            "data": mock_audio_data
        })

        response = websocket.receive_json()

        assert response["mime_type"] == "audio/pcm"
        assert response["data"] == "ZmFrZWRhdGE="
