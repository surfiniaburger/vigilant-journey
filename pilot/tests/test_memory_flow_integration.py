import pytest
import os
import uuid
from database.local_postgres import get_local_postgres_session_service
from google.adk.events import Event
from google.genai.types import Content, Part

@pytest.mark.integration
@pytest.mark.asyncio
async def test_postgres_session_persistence():
    """
    Verifies that a session created in one service instance can be 
    retrieved by another, proving data persistence in Postgres.
    
    Requires: Local Postgres running (docker-compose up).
    """
    # 1. Setup
    # We use the factory which pulls from env vars (defaults to localhost:5432)
    service_1 = get_local_postgres_session_service()
    
    # Create a unique session
    user_id = f"test_user_{uuid.uuid4()}"
    app_name = "IntegrationTestApp"
    
    session = await service_1.create_session(app_name=app_name, user_id=user_id)
    session_id = session.id
    
    # 2. Act - Add an event
    event = Event(
        author="user",
        content=Content(parts=[Part(text="Hello Postgres!")])
    )
    await service_1.append_event(session, event)
    
    # 3. Assert - Create a NEW service instance and retrieve the session
    # This proves the data isn't just in service_1's memory
    service_2 = get_local_postgres_session_service()
    print(f"DEBUG: Calling get_session with session_id={session_id}")
    retrieved_session = await service_2.get_session(session_id=session_id, app_name=app_name, user_id=user_id)
    
    assert retrieved_session is not None
    assert retrieved_session.id == session_id
    assert len(retrieved_session.events) == 1
    assert retrieved_session.events[0].content.parts[0].text == "Hello Postgres!"
    
    # Cleanup
    print("DEBUG: Cleaning up session...")
    await service_1.delete_session(session_id=session_id, app_name=app_name, user_id=user_id)
