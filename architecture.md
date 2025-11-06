# Proposed Agent Architecture

This document outlines a new, modular architecture for the Alora agent system.

## Overview

The proposed architecture separates the user interface (voice and text) from the core agent capabilities (research, map manipulation). This is achieved by creating a set of independent, A2A-connected agents, each with a specific responsibility. This design promotes modularity, scalability, and easier maintenance.

## Components

### 1. Frontend (`mooncake`)

The Next.js application that provides the user interface. It will have two modes of interaction:

-   **Voice Interaction:** The existing voice interface, which will connect to the Voice Agent.
-   **Text Interaction:** A new text-based interface, which will connect to the Text Agent.

### 2. Voice Agent (A2A Service)

A dedicated agent that handles voice input and output.

-   **Responsibility:** Manages the streaming audio connection with the frontend, performs speech-to-text and text-to-speech, and communicates with the Router Agent.
-   **Type:** Streaming agent.

### 3. Text Agent (A2A Service)

A new, dedicated agent that handles text-based interactions.

-   **Responsibility:** Provides a simple, request/response API for text-based chat. It will receive text from the frontend and forward it to the Router Agent.
-   **Type:** Non-streaming, request/response agent.

### 4. Router Agent (A2A Service)

A new agent that acts as a central orchestrator.

-   **Responsibility:** Receives requests from both the Voice and Text Agents. It analyzes the user's intent and decides which specialized agent to call (e.g., Research Agent, Dora Agent).
-   **Type:** Non-streaming, request/response agent.

### 5. Research Agent (A2A Service)

The existing "research flow" extracted into its own A2A service.

-   **Responsibility:** Handles all research-related tasks, such as searching the web and answering questions.
-   **Type:** Non-streaming, request/response agent.

### 6. Dora Agent (A2A Service)

The agent responsible for map manipulation, extracted into its own A2A service.

-   **Responsibility:** Handles all map-related commands, such as setting the map center.
-   **Type:** Non-streaming, request/response agent.

## Interaction Flow

### Voice Interaction

1.  The user speaks into the frontend.
2.  The frontend streams the audio to the **Voice Agent**.
3.  The **Voice Agent** performs speech-to-text and sends the transcribed text to the **Router Agent**.
4.  The **Router Agent** analyzes the request and calls the appropriate specialized agent (e.g., **Research Agent** or **Dora Agent**).
5.  The specialized agent processes the request and returns the result to the **Router Agent**.
6.  The **Router Agent** forwards the result to the **Voice Agent**.
7.  The **Voice Agent** performs text-to-speech and streams the audio response back to the frontend.

### Text Interaction

1.  The user types a message into the frontend.
2.  The frontend sends the text message to the **Text Agent**.
3.  The **Text Agent** forwards the request to the **Router Agent**.
4.  The **Router Agent** analyzes the request and calls the appropriate specialized agent.
5.  The specialized agent processes the request and returns the result to the **Router Agent**.
6.  The **Router Agent** forwards the result to the **Text Agent**.
7.  The **Text Agent** sends the text response back to the frontend.

## Implementation Milestones

Here is a proposed plan to implement this new architecture:

1.  **Milestone 1: Revert and Clean Up:**
    -   Revert the changes in `mooncake/app/map/page.tsx`.
    -   Uninstall `dompurify`.

2.  **Milestone 2: Create the Text Agent:**
    -   Create a new directory for the text agent.
    -   Define the text agent and its API endpoint.

3.  **Milestone 3: Create the Router Agent:**
    -   Create a new directory for the router agent.
    -   Define the router agent and its API endpoint.

4.  **Milestone 4: Connect Agents:**
    -   Connect the Text Agent to the Router Agent.
    -   Modify the Voice Agent to call the Router Agent.

5.  **Milestone 5: Modularize Sub-Agents:**
    -   Extract the Research Agent and Dora Agent into their own A2A services.
    -   Update the Router Agent to call these new services.

