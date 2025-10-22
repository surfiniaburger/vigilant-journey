# Pilot: The Alora Backend & Voice Agent

Pilot is the core of the Alora AI Co-Pilot. It's a multi-agent system built with the Google Agent Development Kit (ADK) that handles the conversation with the user, processes their requests, and communicates with other services to get information.

## Architecture

The backend is designed as a hierarchical structure of agents, each with a specific role:

*   **`OrchestratorAgent` (Root Agent):** The main entry point for all user interactions. It greets the user and delegates the actual work to the `MainWorkflowAgent`.
*   **`MainWorkflowAgent` (Sequential Agent):** Defines the core logic of the application. It executes a sequence of sub-agents in a specific order: first the `ResearcherAgent`, then the `SessionSummarizerAgent`.
*   **`ResearcherAgent`:** This is the workhorse of the system. It uses a variety of tools to answer the user's query. It can recall information from memory, perform a Google search, and connect to an MCP server to get specific information.
*   **`SessionSummarizerAgent`:** After the `ResearcherAgent` has done its job, this agent creates a concise summary of the conversation and saves it to memory for future reference.

## Getting Started

### Prerequisites

*   Python and uv
*   Google Cloud SDK
*   MongoDB

### Installation

1.  **Install dependencies:**
    ```bash
    uv pip install -e .
    ```

2.  **Set Environment Variables:**
    Create a `.env` file and add the necessary environment variables (e.g., `GOOGLE_CLOUD_PROJECT`, `MONGO_DB_CONNECTION_STRING`).

### Running Locally

```bash
GOOGLE_APPLICATION_CREDENTIALS="./pilot-local-dev-sa-key.json" uv run uvicorn main:app --reload
```
