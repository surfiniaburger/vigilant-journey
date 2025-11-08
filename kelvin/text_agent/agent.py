from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from google.adk.models.lite_llm import LiteLlm

# Placeholder tool for forwarding to the Router Agent
def forward_to_router(user_message: str) -> str:
    """
    Forwards the user's message to the Router Agent for processing.
    This is a placeholder and will be replaced with actual A2A communication.
    """
    print(f"Forwarding message to Router Agent: {user_message}")
    # In a real implementation, this would make an A2A call to the Router Agent
    return f"Message '{user_message}' received and forwarded to Router Agent."

root_agent = Agent(
    model=LiteLlm(model="ollama/gpt-oss:20b-cloud"),
    name='KelvinTextAgent',
    description='A text-based agent that receives user messages and forwards them to the Router Agent.',
    instruction=(
        "You are Kelvin, a text-based assistant. Your primary role is to receive "
        "text messages from the user and forward them to the Router Agent for "
        "further processing. Use the 'forward_to_router' tool to send the user's "
        "message to the Router Agent. Do not attempt to answer questions yourself."
    ),
    tools=[FunctionTool(func=forward_to_router)],
)
