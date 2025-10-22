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
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools import google_search, preload_memory_tool
from .memory_tool import save_memory_tool, recall_memory_tool
from .mcp_tools import mcp_tools
#from .memory_callback import auto_save_session_to_memory_callback
from callbacks import (
    before_agent_callback,
    after_agent_callback,
    before_model_callback,
    after_model_callback,
    before_tool_callback,
    after_tool_callback,
)

# The Researcher Agent: Specializes in using tools to find information.
researcher_agent = Agent(
    name="ResearcherAgent",
    model="gemini-live-2.5-flash-preview-native-audio",
    description="Researches user queries using memory and web search.",
    instruction="""
    You are a helpful research assistant for the Alora car co-pilot.
    Your goal is to fully answer the user's request from the conversation history.
    Use your tools (`recall_memory`, `google_search`, `mcp_tools`) to find the information, then synthesize the results into a final, helpful answer.
    """,
    
    tools=[recall_memory_tool, google_search, mcp_tools],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)

# The Summarizer Agent: Specializes in saving a summary of the conversation.
session_summarizer_agent = Agent(
    name="SessionSummarizerAgent",
    model="gemini-live-2.5-flash-preview-native-audio",
    description="Summarizes the conversation and saves it to memory.",
    instruction="""Review the conversation history. Create a concise, one-sentence summary of the key outcomes. Call the `save_memory_tool` to save this summary under the topic 'conversation_summary'.
    Finally, output a friendly closing message to the user, like 'Is there anything else I can help you with?'""",
    tools=[save_memory_tool],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)

# The Main Workflow Agent: Defines the sequence of research and summarization.
main_workflow_agent = SequentialAgent(
    name="MainWorkflowAgent",
    description="Handles the main workflow: researching a user's request and then summarizing the session.",
    sub_agents=[
        researcher_agent, 
        session_summarizer_agent
    ],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
)

from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

dora_agent = RemoteA2aAgent(
    name="dora_agent",
    description="Agent that can answer questions about maps and places.",
    agent_card="http://localhost:8001/a2a/dora_agent/.well-known/agent.json",
)

# The Orchestrator (Root Agent): Manages the entire interaction and the stream.
root_agent = Agent(
    name="OrchestratorAgent",
    model="gemini-live-2.5-flash-preview-native-audio",
    description="The central AI co-pilot for the vehicle. Greets the user and orchestrates the main workflow.",
    instruction="""You are Alora, the master AI co-pilot for a vehicle.

    1.  First, greet the user warmly and ask how you can help.
    2.  Check the session state for the 'user_prompt'.
    3.  If the prompt contains keywords like 'find', 'where is', or 'show me on the map', your ONLY job is to call your sub-agent, `dora_agent`, to handle the request.
    4.  Otherwise, your ONLY job is to call your sub-agent, `MainWorkflowAgent`, to handle the request.
    5.  You will stream all events from the called sub-agent back to the user. Do NOT generate any other text or try to answer the question yourself.
    """,
    tools=[preload_memory_tool.PreloadMemoryTool()],
    sub_agents=[main_workflow_agent, dora_agent],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)
