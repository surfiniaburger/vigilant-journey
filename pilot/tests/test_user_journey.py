import pytest
import uuid
import asyncio
from database.local_postgres import get_local_postgres_session_service
from google.adk.events import Event
from google.genai.types import Content, Part

@pytest.mark.integration
@pytest.mark.asyncio
async def test_complex_user_journey():
    """
    Simulates a multi-turn user journey to verify Short-Term Memory (Context) persistence
    across service restarts.
    
    Scenario:
    1. User introduces themselves and their car (Mercedes W124).
    2. User adds detail about the car (Green).
    3. Session is "reloaded" (simulated by new Service instance).
    4. We verify the full history is available for the Agent to "see".
    """
    # 1. Setup Session
    try:
        service = get_local_postgres_session_service()
    except Exception:
        pytest.skip("Local Postgres not available - Skipping integration test")

    user_id = f"journey_user_{uuid.uuid4()}"
    app_name = "JourneyApp"
    
    session = await service.create_session(app_name=app_name, user_id=user_id)
    session_id = session.id

    # 2. Turn 1: Introduction
    # User: "Hi, I'm Lewis."
    event1 = Event(author="user", content=Content(parts=[Part(text="Hi, I'm Lewis.")]))
    await service.append_event(session, event1)
    
    # 3. Turn 2: Fact A
    # User: "I drive a 1990 Mercedes W124."
    event2 = Event(author="user", content=Content(parts=[Part(text="I drive a 1990 Mercedes W124.")]))
    await service.append_event(session, event2)

    # 4. Turn 3: Fact B (Edge Case: Disconnected detail)
    # User: "It is painted Signal Red."
    event3 = Event(author="user", content=Content(parts=[Part(text="It is painted Signal Red.")]))
    await service.append_event(session, event3)

    # --- SESSION INTERRUPTION / RESTART ---
    # Simulate app restart by creating a fresh service instance
    new_service = get_local_postgres_session_service()
    
    # 5. Retrieval & Verification
    restored_session = await new_service.get_session(session_id=session_id, app_name=app_name, user_id=user_id)
    history = restored_session.events

    # Verify integrity
    assert len(history) == 3
    assert history[0].content.parts[0].text == "Hi, I'm Lewis."
    assert "W124" in history[1].content.parts[0].text
    assert "Signal Red" in history[2].content.parts[0].text

    # 6. Turn 4: "Agent" recalls context (Simulated)
    # If the agent were running, it would read 'history' to answer "What color is my car?"
    # We verify the data is present for the agent to do so.
    context_string = "\\n".join([e.content.parts[0].text for e in history])
    assert "Signal Red" in context_string
    assert "Mercedes W124" in context_string
    
    print("DEBUG: Complex journey history verified successfully.")
    
    # Cleanup
    await new_service.delete_session(session_id=session_id, app_name=app_name, user_id=user_id)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_memory_edge_case_rapid_updates():
    """
    Edge Case: Rapid fire messages verifying they remain in order in the DB.
    """
    try:
        service = get_local_postgres_session_service()
    except Exception:
        pytest.skip("Local Postgres not available - Skipping integration test")

    user_id = f"speed_user_{uuid.uuid4()}"
    app_name = "SpeedApp"
    session = await service.create_session(app_name=app_name, user_id=user_id)
    
    messages = ["One", "Two", "Three", "Four", "Five"]
    
    # Ingest rapidly
    for msg in messages:
        event = Event(author="user", content=Content(parts=[Part(text=msg)]))
        await service.append_event(session, event)
    
    # Retrieve
    new_service = get_local_postgres_session_service()
    restored = await new_service.get_session(session_id=session.id, app_name=app_name, user_id=user_id)
    
    # Check Order
    retrieved_msgs = [e.content.parts[0].text for e in restored.events]
    assert retrieved_msgs == messages
    
    await new_service.delete_session(session_id=session.id, app_name=app_name, user_id=user_id)
