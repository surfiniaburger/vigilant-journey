from google.adk.tools.tool_context import ToolContext

def add_prompt_to_state(
    tool_context: ToolContext, prompt: str
) -> dict[str, str]:
    """Saves the user's initial prompt to the session state."""
    tool_context.state["USER_PROMPT"] = prompt
    return {"status": "success"}
