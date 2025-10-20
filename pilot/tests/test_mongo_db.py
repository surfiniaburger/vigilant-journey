
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from database.mongo_db import MongoSessionService, get_mongo_session_service
from google.adk.sessions.session import Session

@pytest.fixture
def mock_motor_client():
    """Fixture to mock the AsyncIOMotorClient and the collection."""
    mock_collection = AsyncMock()
    client = MagicMock()
    client.get_database.return_value.get_collection.return_value = mock_collection
    return client, mock_collection

@pytest.mark.asyncio
async def test_create_session(mock_motor_client):
    """Test creating a session."""
    client, collection_mock = mock_motor_client
    session_service = MongoSessionService(client)
    
    session = await session_service.create_session("test_app", "test_user")

    assert isinstance(session, Session)
    assert session.app_name == "test_app"
    assert session.user_id == "test_user"
    collection_mock.insert_one.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_session(mock_motor_client):
    """Test getting a session."""
    client, collection_mock = mock_motor_client
    session_service = MongoSessionService(client)
    collection_mock.find_one.return_value = {
        "session_id": "test_session_id",
        "app_name": "test_app",
        "user_id": "test_user",
    }

    session = await session_service.get_session("test_session_id")

    assert isinstance(session, Session)
    assert session.id == "test_session_id"
    collection_mock.find_one.assert_awaited_once_with({"session_id": "test_session_id"})

@pytest.mark.asyncio
async def test_update_session(mock_motor_client):
    """Test updating a session (which is a no-op)."""
    client, collection_mock = mock_motor_client
    session_service = MongoSessionService(client)

    session = Session(id="test_session_id", app_name="test_app", user_id="test_user")
    await session_service.update_session(session)

    collection_mock.update_one.assert_not_called()

@pytest.mark.asyncio
async def test_delete_session(mock_motor_client):
    """Test deleting a session."""
    client, collection_mock = mock_motor_client
    session_service = MongoSessionService(client)

    await session_service.delete_session("test_session_id")

    collection_mock.delete_one.assert_awaited_once_with({"session_id": "test_session_id"})


@pytest.mark.asyncio
@patch("database.mongo_db.connect_to_mongodb", new_callable=AsyncMock)
async def test_get_mongo_session_service(mock_connect_to_mongodb):
    """Test getting the mongo session service asynchronously."""
    mock_motor_client = MagicMock()
    mock_connect_to_mongodb.return_value = (mock_motor_client, None, None, None)
    
    session_service = await get_mongo_session_service()
    
    assert isinstance(session_service, MongoSessionService)
    assert session_service.client == mock_motor_client
    mock_connect_to_mongodb.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_sessions(mock_motor_client):
    """Test listing sessions."""
    client, collection_mock = mock_motor_client
    session_service = MongoSessionService(client)

    mock_sessions_data = [
        {"session_id": "s1", "app_name": "test_app", "user_id": "u1"},
        {"session_id": "s2", "app_name": "test_app", "user_id": "u2"},
    ]
    
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = mock_sessions_data
    collection_mock.find = MagicMock(return_value=mock_cursor)

    sessions = await session_service.list_sessions("test_app")

    assert len(sessions) == 2
    assert all(isinstance(s, Session) for s in sessions)
    assert sessions[0].id == "s1"
    assert sessions[1].user_id == "u2"
    collection_mock.find.assert_called_once_with({"app_name": "test_app"})
    mock_cursor.to_list.assert_awaited_once_with(length=None)
