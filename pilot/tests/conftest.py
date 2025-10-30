# In tests/conftest.py

import sys
from unittest.mock import MagicMock
import pytest

# --- Step 1: Mock low-level dependencies BEFORE they are imported ---
# Mock the motor module to prevent database connection attempts during testing.
# This must be done at the very top.
sys.modules['motor'] = MagicMock()
sys.modules['motor.motor_asyncio'] = MagicMock()


# --- Step 2: Create a fixture that patches the memory service dependency ---
@pytest.fixture(scope="function", autouse=True)
def mock_memory_service_getter(monkeypatch):
    """
    This fixture runs once per test session and automatically applies its patch.
    It replaces the `get_memory_service` function in `main.py` with a mock
    before any other code (like agent.py) tries to import and call it.
    """
    # Create a single mock memory service for the entire test session.
    mock_service_instance = MagicMock()

    # This fake function will be called by agent.py instead of the real one.
    def fake_get_memory_service():
        return mock_service_instance

    # Patch the `get_memory_service` function in the `main` module.
    monkeypatch.setattr("main.get_memory_service", fake_get_memory_service)
    
    # We can optionally return the mock instance if a test ever needs to inspect it.
    return mock_service_instance


# --- Step 3: Now that dependencies are mocked, we can safely import agent code ---
from google_search_agent.agent import create_root_agent


# --- Step 4: Define fixtures that provide the agent instances to the tests ---
@pytest.fixture(scope="function")
def root_agent(mock_memory_service_getter):
    """
    Creates a single `root_agent` instance for the entire test session.
    It uses the `mock_memory_service_getter` fixture to ensure the dependency
    is already patched before this runs. The factory is called with the mock service.
    """
    # The `mock_memory_service_getter` fixture returns the mock instance we created.
    # We pass this mock into our agent factory.
    return create_root_agent(mock_memory_service_getter, use_mcp_tools=False)


@pytest.fixture(scope="function")
def main_workflow_agent(root_agent):
    """
    Extracts the `main_workflow_agent` from the `root_agent` fixture.
    """
    # The main_workflow_agent is wrapped in the second tool of the root_agent
    # (The first tool is PreloadMemoryTool).
    main_workflow_tool = root_agent.tools[1]
    return main_workflow_tool.agent