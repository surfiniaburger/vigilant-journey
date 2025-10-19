
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from database.mongo_db import MongoSessionService, get_mongo_session_service
from google.adk.sessions.session import Session

@pytest.fixture
def mock_mongo_client():
    """Fixture to mock the MongoDB client."""
    client = MagicMock()
    client.get_database.return_value.get_collection.return_value = MagicMock()
    return client

@pytest.mark.asyncio
async def test_create_session(mock_mongo_client):
    """Test creating a session."""
    session_service = MongoSessionService(mock_mongo_client)
    session_service.sessions.insert_one = AsyncMock()
    session_service.list_sessions = AsyncMock()

    session = await session_service.create_session("test_app", "test_user")

    assert isinstance(session, Session)
    assert session.app_name == "test_app"
    assert session.user_id == "test_user"
    session_service.sessions.insert_one.assert_called_once()

@pytest.mark.asyncio
async def test_get_session(mock_mongo_client):
    """Test getting a session."""
    session_service = MongoSessionService(mock_mongo_client)
    session_service.list_sessions = AsyncMock()
    session_service.sessions.find_one = AsyncMock(return_value={
        "session_id": "test_session_id",
        "app_name": "test_app",
        "user_id": "test_user",
        "metadata": {}
    })

    session = await session_service.get_session("test_session_id")

    assert isinstance(session, Session)
    assert session.id == "test_session_id"
    session_service.sessions.find_one.assert_called_once_with({"session_id": "test_session_id"})

@pytest.mark.asyncio
async def test_update_session(mock_mongo_client):
    """Test updating a session."""
    session_service = MongoSessionService(mock_mongo_client)
    session_service.sessions.update_one = AsyncMock()
    session_service.list_sessions = AsyncMock()

    session = Session(id="test_session_id", app_name="test_app", user_id="test_user")
    await session_service.update_session(session)

    session_service.sessions.update_one.assert_not_called()

@pytest.mark.asyncio
async def test_delete_session(mock_mongo_client):
    """Test deleting a session."""
    session_service = MongoSessionService(mock_mongo_client)
    session_service.sessions.delete_one = AsyncMock()
    session_service.list_sessions = AsyncMock()

    await session_service.delete_session("test_session_id")

    session_service.sessions.delete_one.assert_called_once_with({"session_id": "test_session_id"})

@patch("database.mongo_db.connect_to_mongodb")
def test_get_mongo_session_service(mock_connect_to_mongodb):
    """Test getting the mongo session service."""
    mock_connect_to_mongodb.return_value = (MagicMock(), None, None, None)
    session_service = get_mongo_session_service()
    assert isinstance(session_service, MongoSessionService)

@pytest.mark.asyncio
async def test_list_sessions(mock_mongo_client):
    """Test listing sessions."""
    session_service = MongoSessionService(mock_mongo_client)
    async def mock_to_list(length=None):
        return [
            {
                "session_id": "test_session_id_1",
                "app_name": "test_app",
                "user_id": "test_user",
                "metadata": {},
            },
            {
                "session_id": "test_session_id_2",
                "app_name": "test_app",
                "user_id": "test_user",
                "metadata": {},
            },
        ]
    
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(side_effect=mock_to_list)
    session_service.sessions.find = MagicMock(return_value=mock_cursor)

    sessions = await session_service.list_sessions("test_app")

    assert isinstance(sessions, list)
    assert len(sessions) == 2
    assert all(isinstance(s, Session) for s in sessions)
    session_service.sessions.find.assert_called_once_with({"app_name": "test_app"})
