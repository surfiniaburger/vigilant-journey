
# Agent Documentation

This document provides an overview of the features and services used in this agent.

## Features

*   **Multi-agent Story Writing:** A multi-agent system that collaboratively writes a story. The agents include a story generator, a critic, a reviser, a grammar checker, and a tone checker.
*   **Long-term Memory:** The agent uses `VertexAiMemoryBankService` to store and retrieve information across sessions.
*   **Configurable Memory Topics:** The memory topics can be configured via environment variables. See the **Configuration** section for more details.
*   **Web Interface:** The agent is exposed through a web interface using FastAPI and WebSockets, allowing for real-time interaction.
*   **Callbacks:** The agent uses the ADK's callback system to log and monitor the entire workflow.

## Services

*   **`google.adk.runners.Runner`:** The main runner for the agent.
*   **`google.adk.sessions.InMemorySessionService`:**  Manages sessions in memory.
*   **`google.adk.memory.VertexAiMemoryBankService`:**  Provides long-term memory for the agent.
*   **`google.adk.agents.LlmAgent`:** The base agent for the individual agents in the system.
*   **`google.adk.agents.LoopAgent`:** Used for the critic-reviser loop.
*   **`google.adk.agents.SequentialAgent`:** Used for the post-processing steps.
*   **`fastapi.FastAPI`:** The web framework used to expose the agent.
*   **`uvicorn`:** The ASGI server used to run the FastAPI application.

## Configuration

*   `MEMORY_TOPICS`: A comma-separated list of managed memory topics to use. The available topics are:
    *   `USER_PERSONAL_INFO`
    *   `USER_PREFERENCES`
    *   `KEY_CONVERSATION_DETAILS`
    *   `EXPLICIT_INSTRUCTIONS`
*   `CUSTOM_MEMORY_TOPICS`: A JSON string of custom memory topics. The format is a list of dictionaries, where each dictionary has a `label` and a `description`. For example:
    ```json
    [
        {
            "label": "business_feedback",
            "description": "Specific user feedback about their experience at the coffee shop. This includes opinions on drinks, food, pastries, ambiance, staff friendliness, service speed, cleanliness, and any suggestions for improvement."
        }
    ]
    ```
