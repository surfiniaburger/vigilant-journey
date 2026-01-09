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
from google.adk.events import Event, EventActions
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
from .telemetry_agent import create_telemetry_agent
from .judge_agent import create_judge_agent
from .vision_agent import create_vision_agent
from .audio_context_tool import audio_context_tool
from .bigquery_tool import bigquery_history_tool
from .ingestion_agent import create_ingestion_agent
from .safety_agent import create_safety_oracle_agent, safety_check_tool

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


# --- High-Fidelity Research Schemas ---
from typing import Literal

class Feedback(BaseModel):
    """Model for providing evaluation feedback on research quality."""
    grade: Literal["pass", "fail"] = Field(
        description="Evaluation result. 'pass' if the research is sufficient, 'fail' if it needs revision."
    )
    comment: str = Field(
        description="Detailed explanation of the evaluation, highlighting strengths and/or weaknesses."
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

class EscalationChecker(BaseAgent):
    """Checks the quality gate and escalates to stop the loop if grade is 'pass'."""

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        grade = state.get("critique_grade")
        
        if grade == "pass":
            logger.info("Quality gate PASSED. Escalating to stop loop.")
            yield Event(
                author=self.name,
                actions=EventActions(escalate=True)
            )
        else:
            logger.info(f"Quality gate FAILED (grade: {grade}). Loop continues.")
            yield Event(author=self.name)

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
    )

    safety_and_compliance_agent = Agent(
        name="SafetyAndComplianceAgent",
        model=INTERNAL_MODEL,
        instruction="Review the text in 'draft_answer'. Evaluate if it is safe, complete, and accurate. Use the `safety_check` tool for an explicit security verification of the content. Your response must be JSON matching the Feedback schema.",
        output_schema=Feedback,
        output_key="research_feedback",
        tools=[safety_check_tool],
        **individual_agent_callbacks,
    )

    # Bridge between LLM Feedback schema and the Decision/Escalation logic
    class FeedbackBridgeAgent(BaseAgent):
        async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
            feedback = ctx.session.state.get("research_feedback", {})
            ctx.session.state["critique"] = "APPROVED" if feedback.get("grade") == "pass" else feedback.get("comment", "REJECTED")
            ctx.session.state["critique_grade"] = feedback.get("grade", "fail")
            yield Event(author=self.name)

    feedback_bridge = FeedbackBridgeAgent(name="FeedbackBridge")

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
    escalation_checker = EscalationChecker(name="EscalationChecker")

    critique_and_refine_loop = LoopAgent(
        name="CritiqueAndRefineLoop",
        sub_agents=[parallel_validator, feedback_bridge, decision_agent, escalation_checker, reviser_agent],
        max_iterations=2,
    )

    session_summarizer_agent = Agent(
        name="SessionSummarizerAgent",
        model=INTERNAL_MODEL,
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
    )

    research_task_tool = agent_tool.AgentTool(
        agent=deep_research_workflow,
    )

    # --- Specialized Telemetry Pipeline ---
    telemetry_agent = create_telemetry_agent(individual_agent_callbacks)
    judge_agent = create_judge_agent(individual_agent_callbacks)

    telemetry_pipeline = SequentialAgent(
        name="TelemetryPipeline",
        sub_agents=[telemetry_agent, judge_agent],
    )

    telemetry_task_tool = agent_tool.AgentTool(
        agent=telemetry_pipeline,
    )

    # --- Specialized Vision Bit ---
    vision_agent = create_vision_agent(individual_agent_callbacks)
    vision_task_tool = agent_tool.AgentTool(agent=vision_agent)

    # --- Specialized Ingestion Bit ---
    ingestion_agent = create_ingestion_agent(individual_agent_callbacks)
    ingestion_task_tool = agent_tool.AgentTool(agent=ingestion_agent)

    # --- Specialized Safety Oracle Bit ---
    safety_oracle_agent = create_safety_oracle_agent(individual_agent_callbacks)
    safety_oracle_tool = agent_tool.AgentTool(agent=safety_oracle_agent)

    intelligence_center_agent = Agent(
        name="IntelligenceCenterAgent",
        model=INTERNAL_MODEL,
        instruction=(
            "You are the Intelligence Center. Your goal is to answer the user's question by fusing multiple domains.\n"
            "1.  **Ingest**: If the user provides a document (PDF, CSV) or image that needs deep parsing/classification, use `IngestionAgent` first.\n"
            "2.  **Memory**: ALWAYS check long-term memory with `recall_memory`.\n"
            "3.  **Recent Context**: If you need situational awareness of the current audio, use `get_recent_audio_context`.\n"
            "4.  **Vision**: If an image is present and requires general scene description (rather than document extraction), use `VisionAgent`.\n"
            "5.  **Telemetry**: If the query relates to vehicle health/telemetry, use `TelemetryPipeline`.\n"
            "6.  **Historical**: If the user asks about historical trends, lap times, or past performance, use `bigquery_history_tool`.\n"
            "7.  **Web Search**: If information is missing, use `DeepResearchWorkflow` for broad web research.\n"
            "Synthesize all inputs (Ingestion, Vision, Telemetry, Audio, Memory, History) into a single, cohesive answer."
        ),
        tools=[
            recall_memory_tool, 
            research_task_tool, 
            telemetry_task_tool, 
            vision_task_tool,
            audio_context_tool,
            bigquery_history_tool,
            ingestion_task_tool
        ],
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
            "3.  **Handoff**: The 'IntelligenceCenterAgent' is responsible for fusing Vision, Telemetry, History, and Audio. "
            "Pass the user's query directly to it.\n"
            "4.  **Final Output**: Present the final answer to the user. "
            "If the user requests JSON output, output ONLY JSON and skip the greeting."
        ),
        tools=[preload_memory_tool.PreloadMemoryTool(), safety_oracle_tool, main_workflow_tool],
        **individual_agent_callbacks,
    )
    
    return root_agent
