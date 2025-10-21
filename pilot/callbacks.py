import logging
from typing import Optional, Dict, Any
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types as genai_types

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def after_agent_callback(callback_context: CallbackContext) -> None:
    """
    This callback runs after every agent turn. We use it as a "safety net"
    to ensure the session is always saved to the Memory Bank for persistence.
    """
    logger.info(f"<== AFTER AGENT: {callback_context.agent_name}")

    # --- MEMORY PERSISTENCE LOGIC ---
    memory_service = callback_context.memory_service
    session = callback_context.invocation_context.session

    # Only save the session if we are at the top-level agent to avoid redundant saves.
    if memory_service and session and callback_context.agent_name == "OrchestratorAgent":
        try:
            # This triggers memory generation in the background. Memory Bank will extract
            # and consolidate meaningful information from the raw session data.
            await memory_service.add_session_to_memory(session)
            logger.info(f"*** Successfully triggered memory generation for session: {session.id} ***")
        except Exception as e:
            logger.error(f"*** FAILED to save session to memory: {e} ***")

# --- The rest of your logging callbacks remain the same ---

async def before_agent_callback(callback_context: CallbackContext) -> None:
    logger.info(f"==> BEFORE AGENT: {callback_context.agent_name}")

async def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> None:
    logger.info(f"--> BEFORE MODEL call for {callback_context.agent_name}")

async def after_model_callback(callback_context: CallbackContext, llm_response: LlmResponse) -> None:
    logger.info(f"<-- AFTER MODEL call for {callback_context.agent_name}")

async def before_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> None:
    logger.info(f"---> BEFORE TOOL: Calling {tool.name} with args: {args}")

async def after_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict[str, Any]) -> None:
    logger.info(f"<--- AFTER TOOL: {tool.name} responded.")