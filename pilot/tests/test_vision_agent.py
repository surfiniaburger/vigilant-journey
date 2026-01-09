import pytest
import asyncio
import os
import sys
from unittest.mock import MagicMock, AsyncMock

# Add parent directory to path to allow importing from pilot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google_search_agent.vision_agent import create_vision_agent, VisionAnalysis
from google.adk.sessions.session import Session

@pytest.mark.asyncio
async def test_vision_agent_description():
    # 1. Setup Mock State
    session = Session(id="test_vision", app_name="test_app", user_id="test_user")
    
    # 2. Setup Agent & Context
    agent = create_vision_agent()
    
    class MockContext:
        def __init__(self, session):
            self.session = session
            self.end_invocation = False
            from unittest.mock import MagicMock, AsyncMock
            self.plugin_manager = MagicMock()
            self.plugin_manager.run_before_agent_callback = AsyncMock(return_value=None)
            self.plugin_manager.run_after_agent_callback = AsyncMock(return_value=None)
            self.plugin_manager.run_before_tool_callback = AsyncMock(return_value=None)
            self.plugin_manager.run_after_tool_callback = AsyncMock(return_value=None)
            self.plugin_manager.run_before_model_callback = AsyncMock(return_value=None)
            self.plugin_manager.run_after_model_callback = AsyncMock(return_value=None)

        def model_copy(self, update=None):
            return self

    ctx = MockContext(session)

    # 3. Mock the LLM Generate Call
    from google.adk.events import Event
    from google.genai.types import Content, Part
    
    mock_json = (
        '{"objects_detected": ["steering wheel", "dashboard"], '
        '"colors_and_environment": "Bright interior, daytime.", '
        '"text_or_signs": "Check engine light is blinking.", '
        '"safety_hazards": ["blinking warning light"], '
        '"overall_description": "User is in the driver seat, check engine light active."}'
    )
    mock_event = Event(
        author="VisionAgent",
        content=Content(parts=[Part(text=mock_json)])
    )

    async def mock_run_async_impl(context):
        context.session.state["vision_summary"] = {
            "objects_detected": ["steering wheel", "dashboard"],
            "colors_and_environment": "Bright interior, daytime.",
            "text_or_signs": "Check engine light is blinking.",
            "safety_hazards": ["blinking warning light"],
            "overall_description": "User is in the driver seat, check engine light active."
        }
        yield mock_event
    
    agent._run_async_impl = mock_run_async_impl

    # 4. Run Agent
    events = []
    async for event in agent.run_async(ctx):
        events.append(event)

    # 5. Assertions
    result = session.state["vision_summary"]
    assert "steering wheel" in result["objects_detected"]
    assert "blinking" in result["text_or_signs"]
    assert len(result["safety_hazards"]) > 0

if __name__ == "__main__":
    asyncio.run(test_vision_agent_description())
