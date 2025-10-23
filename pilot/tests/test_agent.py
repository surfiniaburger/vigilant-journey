# In tests/test_agent.py

# Remove the direct imports of the agent instances
# from google_search_agent.agent import root_agent, main_workflow_agent
from google.adk.tools import google_search


# Your tests now accept the agent fixtures as arguments
def test_agent_name(root_agent):
    assert root_agent.name == "OrchestratorAgent"


def test_agent_model(root_agent):
    # It's better practice to check if the model name is in the expected string
    # in case of minor version changes.
    assert "gemini-live-2.5-flash-preview-native-audio" in root_agent.model


def test_agent_description(root_agent):
    assert root_agent.description == "The central AI co-pilot for the vehicle, Alora."


def test_agent_instruction(root_agent):
    expected_instruction = (
        "You are Alora, the friendly and helpful AI co-pilot for the vehicle. "
        "Greet the user. When the user asks a question, you MUST use the "
        "'MainWorkflowAgent' tool to find the answer. Once the tool returns the "
        "final answer, present that answer back to the user in a clear and "
        "conversational way. Your role is to be the final interface to the user, "
        "using your internal workflow tool to fulfill their request."
    )
    assert root_agent.instruction == expected_instruction


# This test is no longer valid because `main_workflow_agent` is not a direct sub_agent.
# It is now a tool. We can write a new test for that.
# def test_agent_sub_agents(root_agent, main_workflow_agent):
#     assert main_workflow_agent in root_agent.sub_agents

def test_agent_has_workflow_tool(root_agent, main_workflow_agent):
    """
    Tests that the root_agent's tool list contains the AgentTool
    which wraps the main_workflow_agent.
    """
    # The root agent should have two tools: PreloadMemoryTool and our AgentTool
    assert len(root_agent.tools) == 2
    
    # The second tool should be our workflow tool
    workflow_tool = root_agent.tools[1]
    
    # Check that the tool's name is correct
    assert workflow_tool.name == "MainWorkflowAgent"
    
    # Check that this tool is indeed wrapping our main_workflow_agent instance
    assert workflow_tool.agent is main_workflow_agent