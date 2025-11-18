# Monte Carlo Simulation MCP Server

This directory contains a self-contained MCP server that exposes the Monte Carlo simulation from the "Hack the Track" project as a tool.

## Setup

1.  **Create and activate a virtual environment:**
    This project uses `uv` for package management. To create a virtual environment, run the following command from the `mcp_server` directory:

    ```bash
    uv venv
    source .venv/bin/activate
    ```

2.  **Install dependencies:**
    Once the virtual environment is activated, install the required dependencies:

    ```bash
    uv pip install -e .
    ```

## Running the Server

To start the MCP server, run the following command from the `mcp_server` directory:

```bash
python3 main.py
```

The first time you run the server, it will automatically download and unzip the necessary race data into the `mcp_server/data` and `mcp_server/unzipped_data` directories. This may take a few minutes depending on your internet connection.

Once the data is processed, the server will start and be ready to accept connections from an MCP client.
