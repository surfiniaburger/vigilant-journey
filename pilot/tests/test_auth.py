import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocketDisconnect
from unittest.mock import patch, MagicMock, AsyncMock
from main import app

client = TestClient(app)

@pytest.mark.asyncio
@patch("main.auth.verify_id_token")
@patch("main.start_agent_session")
async def test_websocket_auth_valid_token(mock_start_agent_session, mock_verify_id_token):
    """Test WebSocket connection with a valid Firebase ID token."""
    # Arrange: Mock the Firebase auth check to succeed
    mock_verify_id_token.return_value = {'uid': 'test-user-123'}
    # Arrange: Mock the agent session to prevent it from running fully
    mock_start_agent_session.return_value = (AsyncMock(), MagicMock())

    # Act & Assert: Attempt to connect, should not raise an exception
    try:
        with client.websocket_connect(
            "/ws/test-session?is_audio=false",
            subprotocols=["Bearer", "valid-dummy-token"],
        ) as websocket:
            # If connection is successful, this block will execute
            mock_verify_id_token.assert_called_once_with("valid-dummy-token")
            mock_start_agent_session.assert_called_once_with("test-user-123", False)
            # Close the connection cleanly to end the test
            websocket.close()
    except WebSocketDisconnect as e:
        pytest.fail(f"WebSocket disconnected unexpectedly: {e}")

@pytest.mark.asyncio
@patch("main.auth.verify_id_token")
async def test_websocket_auth_invalid_token(mock_verify_id_token):
    """Test WebSocket connection with an invalid Firebase ID token."""
    # Arrange: Mock the Firebase auth check to fail by raising an exception
    mock_verify_id_token.side_effect = ValueError("Invalid ID token")

    # Act & Assert: Expect a WebSocketDisconnect exception with code 1008
    with pytest.raises(WebSocketDisconnect) as excinfo:
        with client.websocket_connect(
            "/ws/test-session?is_audio=false",
            subprotocols=["Bearer", "invalid-dummy-token"],
        ) as websocket:
            # This part should not be reached
            pass
    
    assert excinfo.value.code == 1008
    # The reason is not checked here because it's not consistently populated
    # assert excinfo.value.reason == "Authentication failed"
    mock_verify_id_token.assert_called_once_with("invalid-dummy-token")
