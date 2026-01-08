import pytest
from unittest.mock import AsyncMock, MagicMock
from google.adk.tools import ToolContext
from google.adk.sessions import Session
from google_search_agent.memory_tool import create_memory_tools

@pytest.mark.asyncio
async def test_memory_tool_flow():
    """
    Verifies the Memory Tool interactions:
    1. Saving a fact (Calls memory_service.add_session_to_memory)
    2. Recalling a fact (Calls memory_service.search_memory)
    3. Handling empty/low-confidence results.
    """
    # 1. Mock the Memory Service
    mock_memory_service = MagicMock()
    # Mock search response
    mock_search_result = MagicMock()
    mock_search_result.memories = [
        MagicMock(content=MagicMock(parts=[MagicMock(text="User likes blue.")]))
    ]
    mock_memory_service.search_memory = AsyncMock(return_value=mock_search_result)
    mock_memory_service.add_session_to_memory = AsyncMock()

    # 2. Create Tools
    save_tool, recall_tool = create_memory_tools(mock_memory_service)
    
    # Mock Context
    session = Session(id="sess_123", app_name="TestApp", user_id="user_456", events=[], state={})
    # Mock Context
    session = Session(id="sess_123", app_name="TestApp", user_id="user_456", events=[], state={})
    ctx = MagicMock()
    ctx.session = session
    ctx.state = {}

    # 3. Test Save Flow
    save_resp = await save_tool.func(ctx, "User likes blue.")
    assert save_resp["status"] == "success"
    mock_memory_service.add_session_to_memory.assert_called_once_with(session)

    # 4. Test Recall Flow (Success)
    recall_resp = await recall_tool.func(ctx, "What does user like?")
    assert recall_resp["status"] == "success"
    assert "User likes blue" in recall_resp["memories"]
    mock_memory_service.search_memory.assert_called_with(
        app_name="TestApp", user_id="user_456", query="What does user like?"
    )

    # 5. Test Recall Flow (Empty/Threshold)
    # Simulate service returning empty list (threshold filter happened in service)
    mock_memory_service.search_memory.return_value = MagicMock(memories=[])
    
    recall_resp_empty = await recall_tool.func(ctx, "Unknown fact?")
    assert recall_resp_empty["status"] == "success"
    assert "No relevant memories found" in recall_resp_empty["memories"]
