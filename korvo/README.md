# Korvo: The Alora MCP Server

Korvo is a Python server built with `FastMCP` that exposes a tool for the Alora AI Co-Pilot to use. It acts as a bridge between the voice agent and the knowledge base for the Mercedes-AMG GT R.

## Features

*   **`ask_amg_manual` Tool:** Exposes a single tool that implements a Retrieval-Augmented Generation (RAG) pipeline to answer questions about the Mercedes-AMG GT R.
*   **Hybrid Search:** Performs a hybrid search (keyword and vector) on an Elasticsearch index containing the car's manual.
*   **Grounded Answers:** Uses the retrieved context and the user's question to generate a grounded answer with the Cohere API.

## Getting Started

### Prerequisites

*   Python and uv
*   Elasticsearch
*   Cohere API Key

### Installation

1.  **Install dependencies:**
    ```bash
    uv pip install -e .
    ```

2.  **Set Environment Variables:**
    Create a `.env` file and add the necessary environment variables (e.g., `ELASTIC_CLOUD_ID`, `ELASTIC_API_KEY`, `COHERE_API_KEY`).

### Running Locally

```bash
uv run --active uvicorn server:app --reload
```