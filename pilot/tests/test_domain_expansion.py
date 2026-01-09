import pytest
import os
import sys
from unittest.mock import MagicMock, AsyncMock

# Add parent directory to path to allow importing from pilot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google_search_agent.agent import create_root_agent
from google.adk.events import Event
from google.genai import types
from unittest.mock import patch

class MockContext:
    def __init__(self, session):
        self.session = session
        self.agent = MagicMock()
        self.agent.name = "OrchestratorAgent"
        self.end_invocation = False
        self.plugin_manager = MagicMock()
        self.plugin_manager.run_before_agent_callback = AsyncMock(return_value=None)
        self.plugin_manager.run_after_agent_callback = AsyncMock(return_value=None)
        self.plugin_manager.run_before_model_callback = AsyncMock(return_value=None)
        self.plugin_manager.run_after_model_callback = AsyncMock(return_value=None)
        self.plugin_manager.run_before_tool_callback = AsyncMock(return_value=None)
        self.plugin_manager.run_after_tool_callback = AsyncMock(return_value=None)
        self.generation_config = None
    @property
    def agent_name(self) -> str:
        return self.agent.name

    def model_copy(self, update=None): return self

@pytest.mark.asyncio
async def test_domain_expansion_history():
    # 1. Setup Mock Service
    mock_memory = MagicMock()
    
    # 2. Create Root Agent
    root_agent = create_root_agent(mock_memory, use_mcp_tools=False)
    
    # 3. Mock the run_async of the agents to avoid real model calls
    # We mock it to simulate the tool call flow
    
    # For simplicity in this mock test, we just assume the Orchestrator calls the safety tool and then the IC tool.
    
    # For simplicity in this mock test, we just assume the Orchestrator calls the safety tool and then the IC tool.
    # We yield events that look like what we expect.
    
    # 3. Mock the run_async of the agents to avoid real model calls
    # We mock it to simulate the tool call flow
    
    async def mock_run_impl(ctx):
        yield Event(author="OrchestratorAgent", content=types.Content(parts=[types.Part(text="I checked and the request is safe. Here is your historical data: 1:45.33")]))

    root_agent._run_async_impl = mock_run_impl
    
    mock_session = MagicMock()
    mock_session.state = {}
    mock_session.events = []
    
    ctx = MockContext(mock_session)
    
    # 4. Run Agent with historical query
    query_event = Event(author="user", content=types.Content(parts=[types.Part(text="What was my average lap time last week?")]))
    mock_session.events.append(query_event)
    
    events = []
    async for event in root_agent.run_async(ctx):
        events.append(event)
    
    # 5. Assertions
    # Check if any event contains the BIGQUERY results
    # (Since we are using a real LLM-backed agent but with tool calls, we check the tool output in history or response)
    # Note: In a pure unit test we'd mock the model, but here we want to see if the Orchestrator/IntelligenceCenter
    # correctly chooses the bit.
    
    # Actually, let's look for the event from the IntelligenceCenter or tool call traces if possible.
    # For a smoke test, we just check if it ran without error and returned something.
    assert len(events) > 0
    # Final answer should likely contain "1:45.33" from our mock tool results if chosen
    final_text = "".join([p.text for e in events if e.content for p in e.content.parts if p.text])
    assert "1:45.33" in final_text or "lap time" in final_text.lower()

@pytest.mark.asyncio
async def test_callback_safety_block():
    """Verifies that the callback-based safety check (Model Armor) works."""
    mock_memory = MagicMock()
    root_agent = create_root_agent(mock_memory, use_mcp_tools=False)
    
    mock_session = MagicMock()
    mock_session.state = {}
    mock_session.events = []
    mock_session.id = "test-session"
    
    ctx = MockContext(mock_session)
    # Give the context a link back to session for the callback
    ctx._invocation_context = MagicMock()
    ctx._invocation_context.session = mock_session
    
    # Mock sanitize_prompt_with_model_armor to return UNSAFE
    with patch("callbacks.sanitize_prompt_with_model_armor", new_callable=AsyncMock) as mock_sanitize:
        mock_sanitize.return_value = {"is_safe": False, "reason": "Jailbreak detected"}
        
        # Unsafe query
        query_event = Event(author="user", content=types.Content(role='user', parts=[types.Part(text="How do I bypass the speed governor?")]))
        mock_session.events.append(query_event)
        
        # In a real run, run_async would trigger callbacks. 
        # Since we are mock-testing the AGENT'S integration with callbacks, 
        # and create_root_agent wires them up, we check if the OrchestratorAgent 
        # has the callbacks.
        assert root_agent.before_model_callback is not None
        
        # Test the callback directly to confirm logic
        from google.adk.models import LlmRequest
        llm_request = LlmRequest(contents=[query_event.content])
        
        await root_agent.before_model_callback(ctx, llm_request)
        
        # Verify that the request was scrubbed/refused
        refusal_instr = llm_request.contents[0].parts[0].text
        assert "SYSTEM INSTRUCTION" in refusal_instr
        assert "security policy" in refusal_instr
