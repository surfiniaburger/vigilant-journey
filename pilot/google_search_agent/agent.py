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

from google.adk.agents import Agent, LoopAgent, ParallelAgent, SequentialAgent
from google.adk.tools import google_search, preload_memory_tool

from .memory_tool import save_memory_tool, recall_memory_tool
from .mcp_tools import mcp_tools
from .knn_validator import knn_validation_tool
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
    instruction="You are a research assistant. Answer the user's request using your tools and store the result in the 'draft_answer' session state key.",
    tools=[recall_memory_tool, google_search, mcp_tools],
    output_key="draft_answer",
)

# --- Dual-Critic Validation Agents (to be run in parallel) ---

safety_and_compliance_agent = Agent(
    name="SafetyAndComplianceAgent",
    model="gemini-live-2.5-flash-preview-native-audio-09-2025",
    instruction="Review the text in 'draft_answer'. If it is safe and complete, respond with 'APPROVED'. Otherwise, provide a critique and store it in the 'critique' session state key.",
    output_key="critique",
)

knn_validator_agent = Agent(
    name="KnnValidatorAgent",
    model="gemini-live-2.5-flash-preview-native-audio-09-2025",
    instruction="You must use the knn_validation_tool to get a confidence score for the text in the 'draft_answer' session state key. Store the score in the 'confidence' session state key.",
    tools=[knn_validation_tool],
    output_key="confidence",
)

parallel_validator = ParallelAgent(
    name="ParallelValidator",
    sub_agents=[safety_and_compliance_agent, knn_validator_agent],
)

# --- Decision Agent (runs after parallel validation) ---

decision_agent = Agent(
    name="DecisionAgent",
    model="gemini-live-2.5-flash-preview-native-audio-09-2025",
    instruction=f"""Examine the session state. If 'critique' is 'APPROVED' and 'confidence' is greater than or equal to {CONFIDENCE_THRESHOLD}, set 'validation_passed' to True. Otherwise, set it to False.""",
    output_key="validation_passed",
)

# --- Reviser Agent (runs if validation fails) ---

reviser_agent = Agent(
    name="ReviserAgent",
    model="gemini-live-2.5-flash-preview-native-audio-09-2025",
    instruction="""Your task is conditional. First, check the 'validation_passed' key in the session state.
    If 'validation_passed' is False, you MUST revise the 'draft_answer' based on the 'critique' to create an improved version. Overwrite the 'draft_answer' with this new version.
    If 'validation_passed' is True, you MUST do nothing and output an empty string to signify your inaction.""",
    output_key="draft_answer",
)

# --- The Refinement Loop ---

critique_and_refine_loop = LoopAgent(
    name="CritiqueAndRefineLoop",
    sub_agents=[parallel_validator, decision_agent, reviser_agent],
    max_iterations=2,
)

# --- The Main Workflow ---

main_workflow_agent = SequentialAgent(
    name="MainWorkflowAgent",
    sub_agents=[researcher_agent, critique_and_refine_loop],
)

# --- Final Output Agent ---

session_summarizer_agent = Agent(
    name="SessionSummarizerAgent",
    model="gemini-live-2.5-flash-preview-native-audio-09-2025",
    instruction="If 'validation_passed' is True, take the final answer from 'draft_answer', save a summary to memory, and present the final answer. If False, inform the user that a high-confidence answer could not be found.",
    tools=[save_memory_tool],
)

# --- The Root Agent ---

root_agent = SequentialAgent(
    name="OrchestratorAgent",
    sub_agents=[main_workflow_agent, session_summarizer_agent],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
)
