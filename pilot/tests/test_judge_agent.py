import pytest
import asyncio
import os
import sys
from unittest.mock import MagicMock, AsyncMock

# Add parent directory to path to allow importing from pilot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google_search_agent.judge_agent import create_judge_agent, JudgeOutput
from google.adk.sessions.session import Session

@pytest.mark.asyncio
async def test_judge_agent_sev1_fail():
    # 1. Setup Mock State
    session = Session(id="test_judge", app_name="test_app", user_id="test_user")
    session.state["telemetry_summary"] = "CRITICAL: Engine temperature is 115C and oil pressure is dropping rapidly. CODE P0117 active."
    
    # 2. Setup Agent & Context
    agent = create_judge_agent()
    
    class MockContext:
        def __init__(self, session):
            self.session = session
            self.end_invocation = False
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
    
    # Simulate JSON output since output_schema is used
    mock_json = '{"grade": "fail", "reasoning": "High engine temperature (115C) exceeds safety limits.", "is_sev1": true}'
    mock_event = Event(
        author="JudgeAgent",
        content=Content(parts=[Part(text=mock_json)])
    )

    async def mock_run_async_impl(context):
        # In a real LlmAgent with output_schema, the content is parsed and put into state
        # We simulate the state update that LlmAgent would perform
        context.session.state["judge_evaluation"] = {
            "grade": "fail",
            "reasoning": "High engine temperature (115C) exceeds safety limits.",
            "is_sev1": True
        }
        yield mock_event
    
    agent._run_async_impl = mock_run_async_impl

    # 4. Run Agent
    events = []
    async for event in agent.run_async(ctx):
        events.append(event)

    # 5. Assertions
    result = session.state["judge_evaluation"]
    assert result["grade"] == "fail"
    assert result["is_sev1"] is True
    assert "115C" in result["reasoning"]

if __name__ == "__main__":
    asyncio.run(test_judge_agent_sev1_fail())
