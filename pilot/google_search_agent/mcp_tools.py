import os
import logging
import google.auth
import google.auth.transport.requests
import google.oauth2.id_token
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the URL of the deployed MCP server from an environment variable
mcp_server_url = os.environ.get("MCP_SERVER_URL")
if not mcp_server_url:
    # Fallback to the URL you provided if the environment variable is not set
    mcp_server_url = "https://alora-mcp-server-140457946058.us-central1.run.app/mcp"

def get_id_token_for_mcp() -> str:
    """Generates a Google-signed ID token to authenticate with the secure MCP server."""
    try:
        # The audience is the root URL of the Cloud Run service
        audience = mcp_server_url.split('/mcp')[0]
        request = google.auth.transport.requests.Request()
        id_token = google.oauth2.id_token.fetch_id_token(request, audience)
        logger.info("Successfully fetched ID token for MCP server.")
        return id_token
    except Exception as e:
        logger.error(f"Failed to fetch ID token for MCP server: {e}")
        raise

# Create the MCPToolset, which will act as a tool for our agent.
# It connects to the remote server and authenticates using the ID token.

mcp_tools = McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=mcp_server_url,
                headers={
                    "Authorization": f"Bearer {get_id_token_for_mcp()}",
                },
            ),
        )
