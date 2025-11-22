import os
import sys
import asyncio
import logging
from fastmcp import FastMCP

# Add the current directory to sys.path to ensure modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monte_carlo_simulation import MonteCarloSimulation
from data_handling.telemetry_parser import parse_telemetry
from gcs_utils import download_directory

# Configure logging
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("Monte Carlo MCP Server 🏎️")

# Constants
PIPELINE_NAME = "mcp-server-pipeline"
SERVING_MODEL_DIR = os.path.join("mcp_server", "serving_model", PIPELINE_NAME)

# Global simulation instance
mc_simulation = None

def initialize_simulation():
    """Initializes the Monte Carlo simulation with models and data."""
    global mc_simulation
    
    # Check for GCS configuration
    gcs_bucket = os.environ.get("GCS_BUCKET_NAME")
    
    if gcs_bucket:
        logger.info(f"GCS_BUCKET_NAME found: {gcs_bucket}. Downloading assets from GCS...")
        try:
            # Define local paths for downloads
            local_assets_dir = os.path.join(os.getcwd(), "downloaded_assets")
            local_model_dir = os.path.join(local_assets_dir, "trained_models")
            local_data_dir = os.path.join(local_assets_dir, "data", "barber")

            # Download models
            logger.info("Downloading models...")
            download_directory(gcs_bucket, "trained_models", local_model_dir)
            
            # Download race data
            logger.info("Downloading race data...")
            download_directory(gcs_bucket, "data/barber", local_data_dir)

            # Update paths to point to downloaded assets
            model_dir_to_use = local_model_dir
            race_data_dir = local_data_dir
            
        except Exception as e:
            logger.error(f"Failed to download assets from GCS: {e}")
            return False
    else:
        logger.info("GCS_BUCKET_NAME not set. Using local assets.")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_dir_to_use = os.path.join(script_dir, "trained_models")
        race_data_dir = os.path.join(script_dir, 'unzipped_data', 'barber-motorsports-park', 'barber')

    logger.info(f"Loading models from: {model_dir_to_use}")
    
    # Load race data
    race_data = parse_telemetry(race_data_dir)
    if race_data is None:
        logger.error("Failed to load race data.")
        return False

    # Initialize Simulation
    try:
        mc_simulation = MonteCarloSimulation(race_data, model_dir=model_dir_to_use)
        logger.info("Monte Carlo Simulation initialized successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize simulation: {e}")
        return False

# Don't initialize on startup - defer to first tool call to allow server to start quickly
# if not initialize_simulation():
#     logger.warning("Simulation failed to initialize. Tools may not work.")

@mcp.tool()
def find_optimal_pit_window(strategy_name: str = None) -> str:
    """
    Uses Monte Carlo simulation to find the optimal pit stop strategy.
    Args:
        strategy_name (str, optional): The name of the specific strategy to run (e.g., "1-stop").
                                       If None, runs all strategies.
    Returns a string describing the best strategy and its average time.
    """
    global mc_simulation
    
    # Lazy initialization on first tool call
    if mc_simulation is None:
        logger.info("Initializing simulation on first tool call...")
        if not initialize_simulation():
            return "Error: Failed to initialize simulation. Check server logs."
    
    return mc_simulation.find_optimal_pit_window(strategy_name)

if __name__ == "__main__":
    # Cloud Run sets PORT environment variable
    port = int(os.getenv("PORT", 8080))
    logger.info(f"🚀 MCP server starting on port {port}")
    
    # Run the server
    # FastMCP handles the HTTP server loop
    mcp.run(transport="sse", port=port, host="0.0.0.0")
