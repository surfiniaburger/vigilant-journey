# Alora: The Mercedes-AMG AI Co-Pilot

Alora is an intelligent, voice-first automotive co-pilot designed to provide drivers with a seamless and intuitive way to interact with their vehicle's features. This project integrates a web-based frontend, a sophisticated multi-agent backend, and a powerful Retrieval-Augmented Generation (RAG) pipeline to answer questions about the Mercedes-AMG GT R.

## How it Works

The application is composed of three main services:

1.  **Frontend (Mooncake):** A Next.js application that provides the user interface for the co-pilot. It uses Firebase for user authentication and establishes a WebSocket connection to the backend to stream communication with the agent.

2.  **Backend/Voice Agent (Pilot):** The core of the application, built with the Google Agent Development Kit (ADK). It's a multi-agent system that orchestrates the conversation with the user. The `ResearcherAgent` is responsible for calling the MCP server to get answers to user questions.

3.  **MCP Server (Korvo):** A Python server built with `FastMCP` that exposes a single tool: `ask_amg_manual`. This tool is a RAG pipeline that answers questions about the Mercedes-AMG GT R. It works by:
    *   Taking a user's question.
    *   Performing a hybrid search (keyword and vector) on an Elasticsearch index containing the car's manual.
    *   Using the retrieved context and the user's question to generate a grounded answer with the Cohere API.

## Deployment

*   **Backend (`pilot`):** Deployed to Cloud Run.
*   **Frontend (`mooncake`):** Deployed to Firebase Hosting.
*   **MCP Server (`korvo`):** Deployed to Cloud Run.

## Getting Started

### Prerequisites

*   Node.js and npm
*   Python and uv
*   Google Cloud SDK
*   Firebase CLI

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/alora.git
    cd alora
    ```

2.  **Install frontend dependencies:**
    ```bash
    npm install --prefix mooncake
    ```

3.  **Install backend dependencies:**
    ```bash
    uv pip install -e ./pilot
    ```

4.  **Install MCP server dependencies:**
    ```bash
    uv pip install -e ./korvo
    ```

### Running Locally

1.  **Set Environment Variables:**
    Create a `.env` file in the `pilot` and `korvo` directories and add the necessary environment variables (e.g., `GOOGLE_CLOUD_PROJECT`, `ELASTIC_CLOUD_ID`, `ELASTIC_API_KEY`, `COHERE_API_KEY`).

2.  **Run the MCP Server:**
    ```bash
    uv run --active uvicorn korvo.server:app --reload
    ```

3.  **Run the Backend:**
    ```bash
    GOOGLE_APPLICATION_CREDENTIALS="./pilot-local-dev-sa-key.json" uv run uvicorn pilot.main:app --reload
    ```

4.  **Run the Frontend:**
    ```bash
    npm run dev --prefix mooncake
    ```