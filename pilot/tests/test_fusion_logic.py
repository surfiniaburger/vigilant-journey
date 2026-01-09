import pytest
import asyncio
import os
import sys
from unittest.mock import MagicMock, AsyncMock

# Add parent directory to path to allow importing from pilot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google_search_agent.agent import create_root_agent
from google.adk.sessions.session import Session
from google.adk.events import Event
from google.genai.types import Content, Part

@pytest.mark.asyncio
async def test_fusion_logic_smoke_and_heat():
    # 1. Setup Session
    session = Session(id="test_fusion", app_name="test_app", user_id="test_user")
    
    # 2. Setup Memory Service Mock
    memory_service = MagicMock()
    
    # 3. Create Root Agent (which contains IntelligenceCenterAgent)
    # We'll use a local mock for the IntelligenceCenterAgent itself to test the orchestration
    from google_search_agent.agent import create_root_agent
    root_agent = create_root_agent(memory_service, use_mcp_tools=False)
    
    # Extract the IntelligenceCenterAgent for isolated testing
    # main_workflow_tool (AgentTool) -> intelligence_center_agent
    ic_tool = root_agent.tools[1] # Orchestrator has [preload, main_workflow]
    ic_agent = ic_tool.agent

    class MockContext:
        def __init__(self, session):
            self.session = session
            self.agent = MagicMock()
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

    # 4. Mock the tools to simulate multi-modal input
    # Tools: 0:recall, 1:research, 2:telemetry, 3:vision, 4:audio
    
    # Mock Recall Memory (No results)
    ic_agent.tools[0].run_async = AsyncMock(return_value="No relevant memory found.")
    
    # Mock Telemetry Pipeline Tool
    # Telemetry shows high heat
    ic_agent.tools[2].run_async = AsyncMock(return_value="Telemetry indicates engine temp at 110C. SAFETY JUDGE: FAIL (Critical Heat).")
    
    # Mock Vision Agent Tool
    # Vision shows smoke
    ic_agent.tools[3].run_async = AsyncMock(return_value="Vision Analysis: I see thick gray smoke billowing from the front hood. Safety hazards: FIRE RISK.")
    
    # Mock Audio Context (Optional)
    ic_agent.tools[4].run_async = AsyncMock(return_value="User transcript: 'What's that smell? Is the car okay?'")

    # 5. Mock the IC Agent's own LLM response (Fusion result)
    mock_fusion_event = Event(
        author="IntelligenceCenterAgent",
        content=Content(parts=[Part(text="CRITICAL EMERGENCY: Telemetry shows an engine overheat (110C) and Vision has confirmed active smoke. Combined with your transcript mentioning a strange smell, this is extremely likely to be an engine fire. PULL OVER IMMEDIATELY.")])
    )
    
    async def mock_run_async_impl(context):
        yield mock_fusion_event
        
    ic_agent._run_async_impl = mock_run_async_impl

    # 6. Run Fusion Test
    events = []
    async for event in ic_agent.run_async(ctx):
        events.append(event)
    
    # 7. Assertions
    response = events[0].content.parts[0].text
    assert "CRITICAL EMERGENCY" in response
    assert "smoke" in response.lower()
    assert "110C" in response
    assert "PULL OVER" in response
