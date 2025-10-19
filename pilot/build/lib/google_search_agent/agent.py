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

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import google_search
from .prompt_tool import add_prompt_to_state
from .memory_tool import save_memory_tool, recall_memory_tool
from .mcp_tools import mcp_tools

# Step 3: The Researcher Agent
# This agent uses the prompt from the state and decides which tool to use.
researcher_agent = Agent(
    name="ResearcherAgent",
    model="gemini-flash-latest",
    description="Researches user queries using memory, car manual expertise, and web search.",
    instruction="""You are a helpful research assistant for the Alora car co-pilot.
    Your goal is to fully answer the user's PROMPT, which is saved in the session state.

    You have access to several tools, in order of priority:
    1. `RecallMemory`: To check for past information about the user.
    2. `ask_amg_manual` (via MCP): An expert tool that consults the car's official operator's manual.
    3. `SaveMemory`: To save important new user preferences.
    4. `google_search`: For general public information NOT related to the car's specific functions.

    **Your process is strict:**
    1.  First, ALWAYS use `RecallMemory` to check for user preferences or past context.
    2.  If the user's PROMPT is about the car's features, warnings, or how to operate something, you MUST use the `ask_amg_manual` tool.
    3.  Only use `google_search` if the question is general knowledge and cannot be answered by the car manual.
    4.  If the user states a new preference, use `SaveMemory` to remember it.

    Synthesize the results from the tools you use into a final, helpful answer.

    USER_PROMPT: {{ USER_PROMPT }}
    """,
    tools=[recall_memory_tool, save_memory_tool, mcp_tools, google_search],
)

# Step 4: The Session Summarizer Agent
# This agent runs at the end to save a summary of the conversation.
session_summarizer_agent = Agent(
    name="SessionSummarizerAgent",
    model="gemini-flash-latest",
    description="Summarizes the conversation and saves it to memory.",
    instruction="""Review the entire conversation history. Create a concise, one-sentence summary of the key outcomes, decisions, or facts learned. 
    Then, call the `SaveMemory` tool to save this summary under the topic 'conversation_summary'.
    Finally, output a friendly closing message to the user, like 'Is there anything else?'""",
    tools=[save_memory_tool],
)

# Step 2: The Main Workflow Agent
# This agent orchestrates the main logic.
main_workflow_agent = SequentialAgent(
    name="MainWorkflowAgent",
    description="The main workflow for handling a user's request.",
    sub_agents=[
        researcher_agent, 
        session_summarizer_agent
    ]
)

# Step 1: The Greeter Agent (Root Agent)
# This is the entry point. It greets, saves the prompt, and transfers control.
root_agent = Agent(
    name="OrchestratorAgent",
    model="gemini-live-2.5-flash-preview-native-audio",
    description="The central AI co-pilot for the vehicle. Greets the user and kicks off the main workflow.",
    instruction="""You are Alora, the master AI co-pilot for a vehicle.
    - Greet the user warmly and ask how you can help.
    - When the user responds, use the 'add_prompt_to_state' tool to save their full request.
    - After saving the prompt, you MUST transfer control to the 'MainWorkflowAgent' agent to handle the request.
    """,
    tools=[add_prompt_to_state],
    sub_agents=[main_workflow_agent]
)
