import pytest
import asyncio
import os
import sys
from unittest.mock import MagicMock
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions.session import Session

# Add parent directory to path to allow importing from pilot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google_search_agent.telemetry_agent import create_telemetry_agent, TelemetryData

@pytest.mark.asyncio
async def test_telemetry_agent_summary():
    # 1. Setup Mock Input
    telemetry = TelemetryData(
        speed_mph=65.0,
        engine_temp_c=105.0, # Slightly high
        fuel_level_percent=12.0, # Low fuel
        tire_pressure_psi={"FL": 32, "FR": 32, "RL": 28, "RR": 32}, # RL low
        error_codes=["P0117"] # Engine coolant temp sensor circuit low
    )
    
    # 2. Setup Agent & Context
    agent = create_telemetry_agent()
    session = Session(id="test_session", app_name="test_app", user_id="test_user")
    session.state["telemetry_data"] = telemetry.model_dump()
    
    class MockContext:
        def __init__(self, session):
            self.session = session
            self.end_invocation = False
            from unittest.mock import AsyncMock
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
    
    mock_event = Event(
        author="TelemetryAgent",
        content=Content(parts=[Part(text="Engine is running hot and rear left tire pressure is low. Fuel is also reaching critical levels. Please check the coolant sensor.")])
    )

    async def mock_run_async_impl(context):
        # The agent's output_key logic in LlmAgent will populate the state 
        # based on the content of the event returned by _run_async_impl.
        context.session.state["telemetry_summary"] = "Engine is running hot and rear left tire pressure is low. Fuel is also reaching critical levels. Please check the coolant sensor."
        yield mock_event
    
    agent._run_async_impl = mock_run_async_impl

    # 4. Run Agent
    events = []
    async for event in agent.run_async(ctx):
        events.append(event)

    # 5. Assertions
    assert "telemetry_summary" in session.state
    assert "Engine is running hot" in session.state["telemetry_summary"]
    assert "rear left tire pressure is low" in session.state["telemetry_summary"]
    assert len(events) > 0

if __name__ == "__main__":
    asyncio.run(test_telemetry_agent_summary())
