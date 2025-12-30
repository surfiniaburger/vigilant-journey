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
#from main import get_memory_service

# --- Configure Logging ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

import os

# --- Constants ---
# --- Constants ---
CONFIDENCE_THRESHOLD = 0.05
LIVE_MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash")
INTERNAL_MODEL = os.getenv("INTERNAL_MODEL", "gemini-2.5-flash")

# --- Authentication Configuration ---
# If running in Cloud Run (GOOGLE_CLOUD_PROJECT is set), we implicitly configure for Vertex AI
# by using the full resource path for the models.
_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")

if _PROJECT and _LOCATION:
    # Transform short model names to full Vertex Resource IDs
    # e.g. "gemini-2.5-flash" -> "projects/PROJECT/locations/LOCATION/publishers/google/models/gemini-2.5-flash"
    
    def _to_vertex_id(model_name):
        if model_name.startswith("projects/"): return model_name
        return f"projects/{_PROJECT}/locations/{_LOCATION}/publishers/google/models/{model_name}"

    LIVE_MODEL = _to_vertex_id(LIVE_MODEL)
    INTERNAL_MODEL = _to_vertex_id(INTERNAL_MODEL)



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

        validation_result = False
        
        critique = state.get("critique")
        # Ensure confidence is a float, defaulting to 0.0 if not present
        try:
            confidence = float(state.get("confidence", 0.0))
        except (ValueError, TypeError):
            confidence = 0.0

        if critique == "APPROVED" and confidence >= CONFIDENCE_THRESHOLD:
            validation_result = True

        # Directly update the session state
        state["validation_passed"] = validation_result
        logger.info(f"Decision made: validation_passed = {validation_result}")
        
        output_text = "VALIDATION_PASSED" if validation_result else "VALIDATION_FAILED"

        # Yield a content event so the framework can populate the output_key
        # We output explicit text so the Summarizer Agent (LLM) can easily see the decision in history
        yield Event(
            author=self.name,
            content=Content(parts=[Part(text=output_text)]),
        )

# --- HELPER FUNCTIONS FOR AGENT CREATION (TIER 1 TESTING) ---
def create_search_agent(callbacks):
    return Agent(
        name="SearchAgent",
        model=INTERNAL_MODEL,
        instruction="You are a search specialist. Search Google for information relevant to the user's request. Output a detailed summary of the key findings. Do not check memory.",
        tools=[google_search],
        output_key="search_results",
        **callbacks,
    )

def create_analysis_agent(tools, callbacks):
    return Agent(
        name="ResearchAnalysisAgent",
        model=INTERNAL_MODEL,
        instruction="You are a research analyst. The message you receive contains search results. Synthesize this information into a final, comprehensive answer. If the search results are empty, say 'No information found'.",
        tools=tools,
        output_key="draft_answer",
        **callbacks,
    )

# --- FACTORY FUNCTION FOR CREATING THE ROOT AGENT ---
def create_root_agent(memory_service, use_mcp_tools: bool = True):
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

    analysis_tools = [recall_memory_tool]
    if use_mcp_tools:
        from .mcp_tools import mcp_tools
        analysis_tools.append(mcp_tools)

    # --- Split Researcher into Search & Analysis to support strict tool rules of Gemini 2.x ---
    
    search_agent = create_search_agent(individual_agent_callbacks)
    analysis_agent = create_analysis_agent(analysis_tools, individual_agent_callbacks)

    researcher_agent = SequentialAgent(
        name="ResearcherAgent",
        sub_agents=[search_agent, analysis_agent],
        before_agent_callback=before_agent_callback,
        after_agent_callback=after_agent_callback,
    )

    safety_and_compliance_agent = Agent(
        name="SafetyAndComplianceAgent",
        model=INTERNAL_MODEL,
        instruction="Review the text in 'draft_answer'. If it is safe, complete, and accurate, output only the word 'APPROVED'. Otherwise, provide a brief critique and place it in the 'critique' session state key.",
        output_key="critique",
        **individual_agent_callbacks,
    )

    knn_validator_agent = Agent(
        name="KnnValidatorAgent",
        model=INTERNAL_MODEL,
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
        instruction="Review the conversation history. Check the output from 'DecisionAgent'. If it says 'VALIDATION_PASSED', you MUST accept the 'draft_answer' and present it to the user as your final answer. Do not hallucinate a refusal. If it says 'VALIDATION_FAILED', inform the user that a high-confidence answer could not be found.",
        tools=[save_memory_tool],
        output_key="final_answer",
        **individual_agent_callbacks,
    )

    deep_research_workflow = SequentialAgent(
        name="DeepResearchWorkflow",
        description="Performs deep research on a topic, verifies facts, and summarizes findings.",
        sub_agents=[
            researcher_agent,
            critique_and_refine_loop,
            session_summarizer_agent,
        ],
        before_agent_callback=before_agent_callback,
        after_agent_callback=after_agent_callback,
    )

    research_task_tool = agent_tool.AgentTool(
        agent=deep_research_workflow,
    )

    intelligence_center_agent = Agent(
        name="IntelligenceCenterAgent",
        model=INTERNAL_MODEL,
        instruction=(
            "You are the Intelligence Center. Your goal is to answer the user's question efficiently.\n"
            "1. ALWAYS checks long-term memory first using `recall_memory`.\n"
            "2. If the answer is found in memory, answer directly. Do NOT perform new research.\n"
            "3. If the answer is NOT in memory, use the `DeepResearchWorkflow` tool to research it."
        ),
        tools=[recall_memory_tool, research_task_tool],
        **individual_agent_callbacks,
    )

    main_workflow_tool = agent_tool.AgentTool(
        agent=intelligence_center_agent,
    )

    # Finally, create and return the root agent
    root_agent = Agent(
        name="OrchestratorAgent",
        model=LIVE_MODEL,
        description="The central AI co-pilot for the vehicle, Alora.",
        instruction=(
            "You are Alora, the friendly and helpful AI co-pilot for the vehicle.\n"
            "1.  **Greeting**: Greet the user primarily in chat contexts.\n"
            "2.  **Tool Usage**: You MUST use the 'IntelligenceCenterAgent' tool to find answers.\n"
            "3.  **Image Analysis**: If the user provides an image:\n"
            "    a. You (Alora) have vision. The 'IntelligenceCenterAgent' tool is BLIND.\n"
            "    b. Describe the image in high detail (what objects, text, colors, etc. you see).\n"
            "    c. Send this *text description* + the user's query to the 'IntelligenceCenterAgent' tool.\n"
            "    d. Do NOT say 'I cannot see the image'. You can! Only the tool cannot.\n"
            "4.  **Final Output**: Present the final answer to the user. "
            "If the user requests JSON output, output ONLY JSON and skip the greeting."
        ),
        tools=[preload_memory_tool.PreloadMemoryTool(), main_workflow_tool],
        **individual_agent_callbacks,
    )
    
    return root_agent
