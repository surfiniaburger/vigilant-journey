
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

import pytest
from google_search_agent.agent import root_agent, main_workflow_agent
from google.adk.tools import google_search
from google_search_agent.prompt_tool import add_prompt_to_state


def test_agent_name():
    assert root_agent.name == "OrchestratorAgent"


def test_agent_model():
    assert root_agent.model == "gemini-live-2.5-flash-preview-native-audio-09-2025"


def test_agent_description():
    assert (
        root_agent.description
        == "The central AI co-pilot for the vehicle. Greets the user and kicks off the main workflow."
    )


def test_agent_instruction():
    expected_instruction = """You are Alora, the master AI co-pilot for a vehicle.
    - Greet the user warmly and ask how you can help.
    - When the user responds, use the 'add_prompt_to_state' tool to save their full request.
    - After saving the prompt, you MUST transfer control to the 'MainWorkflowAgent' agent to handle the request.
    """
    assert root_agent.instruction == expected_instruction


def test_agent_tools():
    assert add_prompt_to_state in root_agent.tools


def test_agent_sub_agents():
    assert main_workflow_agent in root_agent.sub_agents
