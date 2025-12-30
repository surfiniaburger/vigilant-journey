import logging
import asyncio
import contextvars
from typing import Optional, Dict, Any
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types as genai_types
from google.genai.types import Content, Part
from security import sanitize_prompt_with_model_armor
import json

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- STREAMING LOGS CONTEXT ---
# This ContextVar holds the asyncio.Queue for the CURRENT request.
# If set, callbacks will push user-friendly log messages to it.
log_queue_var: contextvars.ContextVar[Optional[asyncio.Queue]] = contextvars.ContextVar("log_queue", default=None)

def _emit_log(message: str):
    """Helper to emit a log message to the current queue if available."""
    queue = log_queue_var.get()
    if queue:
        # We push a dict that will be JSON-serialized later
        try:
            queue.put_nowait({"log": message})
        except asyncio.QueueFull:
            pass # Should not happen with unbounded queue

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
            _emit_log("🧠 Consolidating Long-Term Memory...")
            await memory_service.add_session_to_memory(session)
            logger.info(f"*** Successfully triggered memory generation for session: {session.id} ***")
            _emit_log("✅ Memory Updated")
        else:
            logger.warning("*** Memory service or session not found in invocation context. Cannot save to memory. ***")

    except Exception as e:
        logger.error(f"*** An unexpected error occurred in after_agent_callback: {e} ***", exc_info=True)


# --- The rest of your logging callbacks remain the same ---

async def before_agent_callback(callback_context: CallbackContext) -> None:
    agent_name = callback_context.agent_name
    logger.info(f"==> BEFORE AGENT: {agent_name}")
    
    # Map Agent Names to User-Friendly Emojis/Text
    if agent_name == "KnnValidatorAgent":
        _emit_log("🏎️ Validating Terminology (Mercedes Jargon)...")
    elif agent_name == "ReviserAgent":
        _emit_log("✍️ Refining Response Tone...")
    elif agent_name == "SessionSummarizerAgent":
        _emit_log("📝 Summarizing Context...")
    elif agent_name == "DeepResearchWorkflow":
        _emit_log("📚 Conducting Deep Research...")
    elif agent_name == "IntelligenceCenterAgent":
        _emit_log("🧠 Routing Query via Intelligence Center...")
    elif agent_name == "OrchestratorAgent":
        _emit_log("🤖 Orchestrating Workflow...")
    else:
        _emit_log(f"🤖 Activating {agent_name}...")

async def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> None:
    logger.info(f"--> BEFORE MODEL call for {callback_context.agent_name}")
    
    # --- SECURITY CHECK ---
    # Run Model Armor check. If it fails, we scrub the prompt to force a refusal.
    # We cannot abort the turn here (callback returns None), so we override the input.
    response = await security_check_callback(callback_context, llm_request)
    if response:
        # Security violation detected. 'response' contains the refusal message.
        # We replace the user's prompt with a system instruction to refuse.
        if llm_request.contents and llm_request.contents[-1].role == 'user':
            refusal_text = response.content.parts[0].text
            logger.warning(f"Security Scrubbing: Replacing unsafe prompt with refusal: {refusal_text}")
            llm_request.contents[-1].parts = [
                Part(text=f"SYSTEM INSTRUCTION: The user's input was blocked by security policy. Respond exactly with: '{refusal_text}'")
            ]

async def after_model_callback(callback_context: CallbackContext, llm_response: LlmResponse) -> None:
    logger.info(f"<-- AFTER MODEL call for {callback_context.agent_name}")

async def before_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> None:
    logger.info(f"---> BEFORE TOOL: Calling {tool.name} with args: {args}")
    # Generic tool logging
    _emit_log(f"🛠️ Using Tool: {tool.name}...")

async def after_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict[str, Any]) -> None:
    logger.info(f"<--- AFTER TOOL: {tool.name} responded.")

# Helper function (internal)
async def security_check_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Checks for security violations using Model Armor.
    Returns an LlmResponse if the request should be blocked.
    """
    # ... logic remains same ...
    # The user prompt is the last content in the request
    if not llm_request.contents:
        return None

    last_content = llm_request.contents[-1]
    if last_content.role != 'user' or not last_content.parts:
        return None

    user_prompt = "".join(part.text for part in last_content.parts if part.text).strip().lower()

    if not user_prompt:
        return None

    # Skip security check for internal context prompts (e.g. from KNN validator or orchestration)
    # These often trigger false positives in RAI filters and are not direct user inputs.
    INTERNAL_PROMPT_PREFIX = "for context:"
    KNN_VALIDATOR_AGENT_TAG = "[knnvalidatoragent]"
    if user_prompt.startswith(INTERNAL_PROMPT_PREFIX) or KNN_VALIDATOR_AGENT_TAG in user_prompt:
        logger.debug("Skipping Model Armor check for internal context prompt.")
        return None

    _emit_log("🛡️ Verifying Safety (Model Armor)...")

    # Use Model Armor for sanitization, await the result
    sanitization_result = await sanitize_prompt_with_model_armor(user_prompt)
    
    if not sanitization_result.get("is_safe"):
        reason = sanitization_result.get("reason", "unspecified security concern")
        logger.warning(
            f"Model Armor blocked prompt in session {callback_context._invocation_context.session.id}. "
            f"Reason: '{reason}'. Prompt: '{user_prompt[:200]}...'"
        )
        _emit_log(f"⛔️ Security Block: {reason}")
        return LlmResponse(
            content=Content(
                parts=[Part(text="Your request could not be processed due to a security policy.")],
                role="model"
            ),
            turn_complete=True
        )
    
    logger.info("Prompt passed Model Armor security check.")
    _emit_log("✅ Safety Check Passed")
    return None