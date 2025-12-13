import pytest
import os
import sys

# Add parent directory to path to allow importing from pilot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google_search_agent.agent import create_search_agent
from google.adk.events import Event
from google.genai.types import Content, Part
from unittest.mock import MagicMock

def test_search_agent_creation():
    """Verify SearchAgent is created with correct configuration."""
    callbacks = {}
    agent = create_search_agent(callbacks)
    
    assert agent.name == "SearchAgent"
    assert "search specialist" in agent.instruction
    assert len(agent.tools) == 1
    assert agent.output_key == "search_results"

@pytest.mark.asyncio
async def test_search_agent_tool_selection():
    """Verify SearchAgent selects google_search tool for a query."""
    # This is a 'shallow' test checking the agent's definition capability
    # In a real environment with a mock LLM, we would check the output event.
    # For now, we verify the tool definition matches expectation.
    
    callbacks = {}
    agent = create_search_agent(callbacks)
    tool = agent.tools[0]
    
    assert tool.name == "google_search"
    # We can inspect the tool's schema if needed to verify args
