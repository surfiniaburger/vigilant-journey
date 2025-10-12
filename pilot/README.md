# Vigilant Journey - Streaming Agent Chat

This is a web-based chat application that features a conversational AI agent powered by Google's Vertex AI and the Agent Development Kit (ADK). The application supports real-time, bidirectional streaming of both text and audio messages over WebSockets.

## Features

*   **Real-time Communication:** Interact with the AI agent in real-time with low latency.
*   **Text and Audio Support:** Send and receive messages in both text and audio formats.
*   **Google Search Integration:** The agent can use Google Search to answer questions about recent events or to look up information.
*   **Long-term Memory:** The agent uses Vertex AI Memory Bank to remember information from previous conversations.
*   **Web-based Interface:** A simple and intuitive web interface for interacting with the agent.

## Technologies Used

### Backend

*   **Python:** The backend is written in Python.
*   **FastAPI:** A modern, fast (high-performance) web framework for building APIs.
*   **Google Cloud Vertex AI:** The AI agent is built on Google's Vertex AI platform.
*   **Google Agent Development Kit (ADK):** The ADK is used to build and run the conversational agent.
*   **WebSockets:** For real-time, bidirectional communication between the client and server.

### Frontend

*   **HTML, CSS, JavaScript:** The frontend is built with standard web technologies.
*   **Web Audio API:** Used for capturing and playing back audio in the browser.

## Getting Started

### Prerequisites

*   Python 3.9+
*   Node.js and npm

### Backend Setup

1.  **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up environment variables:**

    Create a `.env` file in the `pilot` directory and add the following:

    ```
    GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    GOOGLE_CLOUD_LOCATION="your-gcp-location"
    AGENT_ENGINE_ID="your-agent-engine-id" # Optional, will be created if not provided
    ```

3.  **Run the backend server:**

    ```bash
    uvicorn main:app --reload
    ```

### Frontend Setup

1.  **Install Node.js dependencies:**

    ```bash
    npm install
    ```

2.  **Run tests (optional):**

    ```bash
    npm test
    ```

## Usage

1.  Open your web browser and navigate to `http://127.0.0.1:8000`.
2.  You can start interacting with the agent by typing messages in the input box and clicking "Send".
3.  To use audio, click the "Start Audio" button. You will be prompted for microphone access. Once enabled, you can speak to the agent and hear its responses.
