
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

from google.adk.tools import google_search
from google_search_agent.agent import root_agent


def test_agent_name():
    assert root_agent.name == "google_search_agent"


def test_agent_model():
    assert root_agent.model in [
        "gemini-live-2.5-flash-preview-native-audio-09-2025",
        "gemini-2.0-flash-live-001",
    ]


def test_agent_description():
    assert root_agent.description == "Agent to answer questions using Google Search."


def test_agent_instruction():
    assert root_agent.instruction == "Answer the question using the Google Search tool."


def test_agent_tools():
    assert google_search in root_agent.tools
