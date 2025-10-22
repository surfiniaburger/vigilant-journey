# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent, LoopAgent
from google.adk.tools import google_search, preload_memory_tool

from .memory_tool import save_memory_tool, recall_memory_tool
from .mcp_tools import mcp_tools
from .knn_validator import knn_validation_tool
from .orchestrator import MasterWorkflowAgent
from callbacks import (
    before_agent_callback,
    after_agent_callback,
    before_model_callback,
    after_model_callback,
    before_tool_callback,
    after_tool_callback,
)

# Confidence threshold for the k-NN validator
CONFIDENCE_THRESHOLD = 0.7

# --- Agent Definitions ---

researcher_agent = Agent(
    name="ResearcherAgent",
    model="gemini-live-2.5-flash-preview-native-audio-09-2025",
    instruction="You are a research assistant. Your goal is to answer the user's request using your tools. Synthesize the results into a final answer and store it in the 'draft_answer' session state key.",
    tools=[recall_memory_tool, google_search, mcp_tools],
    output_key="draft_answer",
)

safety_and_compliance_agent = Agent(
    name="SafetyAndComplianceAgent",
    model="gemini-live-2.5-flash-preview-native-audio-09-2025",
    instruction="Review the text in 'draft_answer'. If it is safe, complete, and accurate, respond with 'APPROVED'. Otherwise, provide a critique and store it in the 'critique' session state key.",
    output_key="critique",
)

dual_critic_validator_agent = Agent(
    name="DualCriticValidatorAgent",
    model="gemini-live-2.5-flash-preview-native-audio-09-2025",
    instruction="You are the final validation authority. First, call the SafetyAndComplianceAgent to perform a qualitative review of the 'draft_answer'. Then, call the knn_validation_tool to get a quantitative confidence score. Consolidate the results. If the qualitative review is 'APPROVED' and the confidence score is above the threshold, set 'validation_passed' to True in the session state. Otherwise, set it to False and store the critique.",
    tools=[safety_and_compliance_agent, knn_validation_tool],
)

reviser_agent = Agent(
    name="ReviserAgent",
    model="gemini-live-2.5-flash-preview-native-audio-09-2025",
    instruction="Revise the text in 'draft_answer' based on the feedback in 'critique' to create an improved version. Overwrite the 'draft_answer' with the new version.",
    output_key="draft_answer",
)


# --- The Refinement Loop ---

critique_and_refine_loop = LoopAgent(
    name="CritiqueAndRefineLoop",
    sub_agents=[researcher_agent, dual_critic_validator_agent, reviser_agent],
    max_iterations=2,
    condition=f"session.state.get('validation_passed') != True"
)

# --- Final Output Agent ---

session_summarizer_agent = Agent(
    name="SessionSummarizerAgent",
    model="gemini-live-2.5-flash-preview-native-audio-09-2025",
    instruction="Review the conversation. If 'validation_passed' is True, take the final answer from 'draft_answer', save a one-sentence summary to memory using save_memory_tool, and present the final answer to the user. If 'validation_passed' is False, inform the user that a high-confidence answer could not be found.",
    tools=[save_memory_tool],
)

# --- The Main Orchestrator ---

main_workflow_agent = MasterWorkflowAgent(
    name="MainWorkflowAgent",
    researcher_agent=critique_and_refine_loop, # The loop is now the main research step
    critique_and_refine_loop=critique_and_refine_loop, # Pass it again to satisfy the Pydantic model
    summarizer_agent=session_summarizer_agent,
)

# --- The Root Agent ---

root_agent = Agent(
    name="OrchestratorAgent",
    model="gemini-live-2.5-flash-preview-native-audio-09-2025",
    description="The central AI co-pilot for the vehicle.",
    instruction="Greet the user, then call the MainWorkflowAgent to handle their request. Stream all events back to the user.",
    tools=[preload_memory_tool.PreloadMemoryTool()],
    sub_agents=[main_workflow_agent],
    **dict(
        before_agent_callback=before_agent_callback,
        after_agent_callback=after_agent_callback,
        before_model_callback=before_model_callback,
        after_model_callback=after_model_callback,
        before_tool_callback=before_tool_callback,
        after_tool_callback=after_tool_callback,
    )
)
