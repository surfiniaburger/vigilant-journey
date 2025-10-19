from unittest.mock import MagicMock
from google.adk.tools.tool_context import ToolContext
from google_search_agent.prompt_tool import add_prompt_to_state

def test_add_prompt_to_state():
    """Test that the add_prompt_to_state tool correctly updates the state."""
    # Create a mock ToolContext with a state dictionary
    mock_state = {}
    mock_tool_context = MagicMock(spec=ToolContext)
    mock_tool_context.state = mock_state

    prompt_text = "This is a test prompt"

    # Call the function
    result = add_prompt_to_state(mock_tool_context, prompt=prompt_text)

    # Assert that the state was updated correctly
    assert mock_tool_context.state.get("USER_PROMPT") == prompt_text

    # Assert that the function returns the expected status
    assert result == {"status": "success"}
