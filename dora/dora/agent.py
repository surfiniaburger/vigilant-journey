import os
import json
from dotenv import load_dotenv
from google.adk.agents import Agent, LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
from mcp import StdioServerParameters

load_dotenv()

# Get the Google Maps API key from an environment variable
google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")

if not google_maps_api_key:
    raise ValueError("GOOGLE_MAPS_API_KEY environment variable not set.")

# Define the MapSearchAgent that uses the Google Maps MCP tool
map_search_agent = LlmAgent(
    name="MapSearchAgent",
    model="gemini-2.5-flash",
    description="Searches for places using Google Maps and returns the location.",
    instruction="""
    You are a map search assistant.
    1.  Take the user's query from the session state under the key 'user_prompt'.
    2.  Use the 'places_text_search' tool to find the location.
    3.  From the tool's output, extract the latitude and longitude of the first result.
    4.  Return a JSON object with the action 'set_map_center' and the lat/lng values.
        Example: { "action": "set_map_center", "lat": 37.7749, "lng": -122.4194 }
    """,
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-google-maps",
                    ],
                    env={
                        "GOOGLE_MAPS_API_KEY": google_maps_api_key
                    }
                ),
            ),
            tool_filter=['places_text_search']
        )
    ],
)

# Define the root agent that orchestrates the workflow
root_agent = LlmAgent(
    name="DoraOrchestrator",
    model="gemini-2.5-flash",
    description="Orchestrates tasks based on user prompts.",
    instruction="""
    You are an orchestrator. Your job is to analyze the user's prompt from the session state (key: 'user_prompt') and delegate to the appropriate tool or agent.

    - If the prompt contains keywords related to maps, location, or finding a place (e.g., "find", "where is", "show me on the map"), call the 'MapSearchAgent'.
    - Otherwise, respond that you can only handle map-related queries.
    """,
    sub_agents=[map_search_agent]
)

# Expose the root agent as an A2A server
a2a_app = to_a2a(root_agent, port=8001)