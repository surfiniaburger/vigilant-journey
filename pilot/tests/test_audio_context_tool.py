import pytest
import asyncio
import os
import sys
from unittest.mock import MagicMock

# Add parent directory to path to allow importing from pilot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google_search_agent.audio_context_tool import get_recent_audio_context
from google.adk.sessions.session import Session
from google.adk.events import Event
from google.genai.types import Content, Part
from google.adk.tools import ToolContext

@pytest.mark.asyncio
async def test_audio_context_retrieval():
    # 1. Setup Session with History
    session = Session(id="test_audio", app_name="test_app", user_id="test_user")
    
    events = [
        Event(author="user", content=Content(parts=[Part(text="Turn on the lights")])),
        Event(author="model", content=Content(parts=[Part(text="Done.")])),
        Event(author="user", content=Content(parts=[Part(text="What is my speed?")])),
    ]
    session.events.extend(events)
    
    # 2. Setup Tool Context Mock
    mock_tool_ctx = MagicMock()
    mock_tool_ctx.invocation_context.session = session

    # 3. Run Tool
    result = await get_recent_audio_context(mock_tool_ctx, limit=2)

    # 4. Assertions
    assert "Turn on the lights" in result
    assert "What is my speed?" in result
    assert "Done." not in result # Model responses should be filtered out
    assert result.count("- ") == 2 # Max limit was 2

if __name__ == "__main__":
    asyncio.run(test_audio_context_retrieval())
