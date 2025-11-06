import logging
from typing import AsyncGenerator

from google.adk.agents import (
    Agent,
    BaseAgent,  # Import BaseAgent to create our custom agent
    LoopAgent,
    ParallelAgent,
    SequentialAgent,
)


from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.tools import agent_tool, google_search, preload_memory_tool
from google.genai.types import Content, Part
from pydantic import BaseModel, Field

# Local Imports
from callbacks import (
    after_agent_callback,
    after_model_callback,
    after_tool_callback,
    before_agent_callback,
    before_model_callback,
    before_tool_callback,
)
from .knn_validator import knn_validation_tool
from .memory_tool import create_memory_tools
from .url_context_tool import url_context_tool
#from main import get_memory_service

# --- Configure Logging ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


# --- Constants ---
CONFIDENCE_THRESHOLD = 0.25
LIVE_MODEL = "gemini-live-2.5-flash-preview-native-audio"
INTERNAL_MODEL = "gemini-2.5-pro"



# --- Input Schema ---
class WorkflowInput(BaseModel):
    user_query: str = Field(
        description="The user's original question that needs to be answered."
    )


# --- NEW: Deterministic Decision Agent (Replaces LLM Agent) ---
class DeterministicDecisionAgent(BaseAgent):
    """A custom, code-driven agent that makes a decision based on session state."""

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        logger.info("Executing deterministic decision logic.")
        state = ctx.session.state

        critique = state.get("critique")
        # Ensure confidence is a float, defaulting to 0.0 if not present
        try:
            confidence = float(state.get("confidence", 0.0))
        except (ValueError, TypeError):
            confidence = 0.0
        
        validation_result = False
        if critique == "APPROVED" and confidence >= CONFIDENCE_THRESHOLD:
            validation_result = True

        # Directly update the session state
        state["validation_passed"] = validation_result
        logger.info(f"Decision made: validation_passed = {validation_result}")

        # Yield a content event so the framework can populate the output_key
        yield Event(
            author=self.name,
            content=Content(parts=[Part(text=str(validation_result))]),
        )

# --- FACTORY FUNCTION FOR CREATING THE ROOT AGENT ---
def create_root_agent(memory_service, use_url_context_tool: bool = True):
    """
    Creates and wires together all agents and tools, using the provided memory service.
    This factory pattern is used to break the circular dependency between main.py and agent.py,
    allowing for isolated testing.
    """
    # Initialize tools that depend on the memory service
    save_memory_tool, recall_memory_tool = create_memory_tools(memory_service)

    # All agent definitions now live inside this factory function
    individual_agent_callbacks = dict(
        before_agent_callback=before_agent_callback,
        after_agent_callback=after_agent_callback,
        before_model_callback=before_model_callback,
        after_model_callback=after_model_callback,
        before_tool_callback=before_tool_callback,
        after_tool_callback=after_tool_callback,
    )

    researcher_tools = [recall_memory_tool, google_search]
    if use_url_context_tool:
        researcher_tools.append(url_context_tool)

    researcher_agent = Agent(
        name="ResearcherAgent",
        model="gemini-2.5-pro",
        instruction=(
            "You are an expert research assistant. Your goal is to comprehensively answer the user's request by following these steps:\n"
            "1. First, use the `google_search` tool to find relevant information and URLs.\n"
            "2. Review the search results. If the snippets provide enough information, synthesize them into a final answer.\n"
            "3. If the query requires more detailed information, select the most relevant URL from the search results and use the `get_info_from_url` tool to get the full content.\n"
            "4. Synthesize all the gathered information into a final, comprehensive answer.\n"
            "5. Place the final answer in the 'draft_answer' session state key."
        ),
        tools=researcher_tools,
        output_key="draft_answer",
        **individual_agent_callbacks,
    )

    safety_and_compliance_agent = Agent(
        name="SafetyAndComplianceAgent",
        model="gemini-2.5-pro",
        instruction="Review the text in 'draft_answer'. If it is safe, complete, and accurate, output only the word 'APPROVED'. Otherwise, provide a brief critique and place it in the 'critique' session state key.",
        output_key="critique",
        **individual_agent_callbacks,
    )

    knn_validator_agent = Agent(
        name="KnnValidatorAgent",
        model="gemini-2.5-pro",
        instruction="Use the knn_validation_tool to get a confidence score for the text in the 'draft_answer' session state key. Output only the final confidence score as a number.",
        tools=[knn_validation_tool],
        output_key="confidence",
        **individual_agent_callbacks,
    )

    parallel_validator = ParallelAgent(
        name="ParallelValidator",
        sub_agents=[safety_and_compliance_agent, knn_validator_agent],
    )

    reviser_agent = Agent(
        name="ReviserAgent",
        model=INTERNAL_MODEL,
        instruction="Revise the text in 'draft_answer' based on the feedback in 'critique' to create an improved version. Overwrite the 'draft_answer' with the new version.",
        output_key="draft_answer",
        **individual_agent_callbacks,
    )

    decision_agent = DeterministicDecisionAgent(name="DecisionAgent")

    critique_and_refine_loop = LoopAgent(
        name="CritiqueAndRefineLoop",
        sub_agents=[parallel_validator, decision_agent, reviser_agent],
        max_iterations=2,
    )

    session_summarizer_agent = Agent(
        name="SessionSummarizerAgent",
        model="gemini-2.5-flash",
        instruction="Review the conversation. If 'validation_passed' is True, take the final answer from 'draft_answer', save a one-sentence summary to memory using save_memory_tool, and present the final answer to the user. If 'validation_passed' is False, inform the user that a high-confidence answer could not be found.",
        tools=[save_memory_tool],
        output_key="final_answer",
        **individual_agent_callbacks,
    )

    main_workflow_agent = SequentialAgent(
        name="MainWorkflowAgent",
        sub_agents=[
            researcher_agent,
            critique_and_refine_loop,
            session_summarizer_agent,
        ],
        before_agent_callback=before_agent_callback,
        after_agent_callback=after_agent_callback,
    )

    main_workflow_tool = agent_tool.AgentTool(
        agent=main_workflow_agent,

    )

    # Finally, create and return the root agent
    root_agent = Agent(
        name="OrchestratorAgent",
        model=LIVE_MODEL,
        description="The central AI co-pilot for the vehicle, Alora.",
        instruction=(
        "You are Alora, the friendly and helpful AI co-pilot for the vehicle. "
        "Greet the user. When the user asks a question, you MUST use the "
        "'MainWorkflowAgent' tool to find the answer. Once the tool returns the "
        "final answer, present that answer back to the user in a clear and "
        "conversational way. Your role is to be the final interface to the user, "
        "using your internal workflow tool to fulfill their request."
        ),
        tools=[preload_memory_tool.PreloadMemoryTool(), main_workflow_tool],
        **individual_agent_callbacks,
    )
    
    return root_agent
