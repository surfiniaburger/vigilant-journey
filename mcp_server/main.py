import asyncio
import os
import pandas as pd

from mcp import types as mcp_types
from mcp.server.lowlevel import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio as mcp_stdio

from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool import adk_to_mcp_tool_type

from data_handling.data_downloader import download_and_move_files
from data_handling.data_loader import unzip_data
from data_handling.telemetry_parser import parse_telemetry
from monte_carlo_simulation import MonteCarloSimulation

# --- Globals ---
app = Server(name="MonteCarloServer")
adk_tool_to_expose = None
mc_simulation = None

# --- MCP Server Handlers ---
@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    """MCP handler to list tools this server exposes."""
    print("MCP Server: Received list_tools request.")
    if adk_tool_to_expose:
        mcp_tool_schema = adk_to_mcp_tool_type(adk_tool_to_expose)
        print(f"MCP Server: Advertising tool: {mcp_tool_schema.name}")
        return [mcp_tool_schema]
    return []

@app.call_tool()
async def call_mcp_tool(
    name: str, arguments: dict
) -> list[mcp_types.Content]:
    """MCP handler to execute a tool call requested by an MCP client."""
    print(f"MCP Server: Received call_tool request for '{name}' with args: {arguments}")
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
    """Initializes and runs the MCP server."""
    global adk_tool_to_expose, mc_simulation
    # 1. Download and unzip data if not already present
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    unzipped_data_dir = os.path.join(script_dir, 'unzipped_data')

    if not os.path.exists(data_dir):
        download_and_move_files(data_dir)
    if not os.path.exists(unzipped_data_dir):
        unzip_data(data_dir, unzipped_data_dir)

    # 2. Load the race data
    # For this example, we'll use the Barber Motorsports Park data.
    race_data_dir = os.path.join(unzipped_data_dir, 'barber-motorsports-park/barber')
    race_data = parse_telemetry(race_data_dir)

    if race_data is None:
        print("Failed to load race data. Exiting.")
        return

    # 3. Initialize the Monte Carlo simulation
    mc_simulation = MonteCarloSimulation(race_data)

    # 4. Create the ADK tool to expose
    adk_tool_to_expose = FunctionTool(
        func=mc_simulation.find_optimal_pit_window,
    )

    # 5. Run the MCP server
    print("Starting MCP Server...")
    try:
        asyncio.run(run_mcp_stdio_server())
    except KeyboardInterrupt:
        print("\nMCP Server (stdio) stopped by user.")
    except Exception as e:
        print(f"MCP Server (stdio) encountered an error: \n{e}")

    print("MCP Server (stdio) process exiting.")

if __name__ == "__main__":
    main()
