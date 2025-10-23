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
    This callback runs after every agent turn. We use it to save the session
    to the Memory Bank for persistence *only after the top-level agent is done*.
    """
    logger.info(f"<== AFTER AGENT: {callback_context.agent_name}")

    # --- MEMORY PERSISTENCE LOGIC ---
    
    # CRITICAL FIX: Only attempt to save the session if the callback is for the
    # top-level OrchestratorAgent. Sub-agents running inside an AgentTool will
    # not have the necessary context and will cause an AttributeError.
    if callback_context.agent_name != "OrchestratorAgent":
        logger.debug(f"Skipping memory save for sub-agent: {callback_context.agent_name}")
        return

    try:
        # Now that we've confirmed we are in the OrchestratorAgent's callback,
        # it is safer to access the invocation_context. We use the private
        # `_invocation_context` as seen in the official notebook for robustness.
        
        invocation_ctx = getattr(callback_context, '_invocation_context', None)
        if not invocation_ctx:
             logger.error("!!! `_invocation_context` not found on `callback_context` for OrchestratorAgent. Cannot save to memory. !!!")
             return

        memory_service = getattr(invocation_ctx, 'memory_service', None)
        session = getattr(invocation_ctx, 'session', None)

        if memory_service and session:
            await memory_service.add_session_to_memory(session)
            logger.info(f"*** Successfully triggered memory generation for session: {session.id} ***")
        else:
            logger.warning("*** Memory service or session not found in invocation context. Cannot save to memory. ***")

    except Exception as e:
        logger.error(f"*** An unexpected error occurred in after_agent_callback: {e} ***", exc_info=True)


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