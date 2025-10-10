import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

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
