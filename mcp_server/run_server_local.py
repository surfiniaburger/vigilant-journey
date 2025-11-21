import asyncio
import os
import sys

# Add the current directory to sys.path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from mcp import types as mcp_types
from mcp.server.lowlevel import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio as mcp_stdio

from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool import adk_to_mcp_tool_type

from mcp_server.data_handling.telemetry_parser import parse_telemetry
from mcp_server.monte_carlo_simulation import MonteCarloSimulation

# --- Globals ---
app = Server(name="MonteCarloServer")
adk_tool_to_expose = None
mc_simulation = None

# --- MCP Server Handlers ---
@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    """MCP handler to list tools this server exposes."""
    # print("MCP Server: Received list_tools request.", file=sys.stderr)
    if adk_tool_to_expose:
        mcp_tool_schema = adk_to_mcp_tool_type(adk_tool_to_expose)
        # print(f"MCP Server: Advertising tool: {mcp_tool_schema.name}", file=sys.stderr)
        return [mcp_tool_schema]
    return []

@app.call_tool()
async def call_mcp_tool(
    name: str, arguments: dict
) -> list[mcp_types.Content]:
    """MCP handler to execute a tool call requested by an MCP client."""
    print(f"MCP Server: Received call_tool request for '{name}' with args: {arguments}", file=sys.stderr)
    if adk_tool_to_expose and name == adk_tool_to_expose.name:
        # We are not passing any arguments to the function, so we can just call it.
        result = adk_tool_to_expose.func()
        return [mcp_types.Content(text=f"Tool {name} completed with result: {result}")]
    return [mcp_types.Content(text=f"Tool {name} not found.")]


# --- Server Initialization ---
async def run_mcp_stdio_server():
    """Runs the MCP server as a stdio server."""
    async with mcp_stdio.stdio_server() as (read_stream, write_stream):
        init_options = InitializationOptions(
            server_name="MonteCarloServer",
            server_version="0.1.0",
            capabilities={},
        )
        await app.run(read_stream, write_stream, init_options)


def main():
    """Initializes and runs the MCP server locally."""
    global adk_tool_to_expose, mc_simulation

    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Use local trained models
    model_dir = os.path.join(script_dir, 'trained_models')
    if not os.path.exists(model_dir):
        print(f"Model directory not found: {model_dir}", file=sys.stderr)
        return

    print(f"Loading models from: {model_dir}", file=sys.stderr)

    # 2. Load the race data
    race_data_dir = os.path.join(script_dir, 'unzipped_data', 'barber-motorsports-park', 'barber')
    if not os.path.exists(race_data_dir):
         print(f"Race data directory not found: {race_data_dir}. Please run prepare_data.py first.", file=sys.stderr)
         return

    race_data = parse_telemetry(race_data_dir) 
    
    if race_data is None:
        print("Failed to load race data. Exiting.", file=sys.stderr)
        return

    # 3. Initialize the Monte Carlo simulation
    mc_simulation = MonteCarloSimulation(race_data, model_dir=model_dir)

    # 4. Create the ADK tool to expose
    adk_tool_to_expose = FunctionTool(
        func=mc_simulation.find_optimal_pit_window,
    )

    # 5. Run the MCP server
    print("Starting MCP Server...", file=sys.stderr)
    try:
        asyncio.run(run_mcp_stdio_server())
    except KeyboardInterrupt:
        print("\nMCP Server (stdio) stopped by user.", file=sys.stderr)
    except Exception as e:
        print(f"MCP Server (stdio) encountered an error: \n{e}", file=sys.stderr)

    print("MCP Server (stdio) process exiting.", file=sys.stderr)

if __name__ == "__main__":
    main()
