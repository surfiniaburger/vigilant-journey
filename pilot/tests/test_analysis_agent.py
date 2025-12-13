import pytest
import os
import sys

# Add parent directory to path to allow importing from pilot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google_search_agent.agent import create_analysis_agent
from google.adk.events import Event
from google.genai.types import Content, Part
from unittest.mock import MagicMock

def test_analysis_agent_creation():
    """Verify ResearchAnalysisAgent is created with correct configuration."""
    callbacks = {}
    mock_tools = [MagicMock()]
    agent = create_analysis_agent(mock_tools, callbacks)
    
    assert agent.name == "ResearchAnalysisAgent"
    assert "research analyst" in agent.instruction
    assert agent.tools == mock_tools
    assert agent.output_key == "draft_answer"
