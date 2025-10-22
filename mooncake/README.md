# Mooncake: The Alora Frontend

Mooncake is the Next.js web application that provides the user interface for the Alora AI Co-Pilot. It's responsible for user authentication, capturing user input (voice and text), and rendering the conversation with the agent.

## Features

*   **User Authentication:** Uses Firebase Authentication to manage user sign-up and sign-in.
*   **Real-time Communication:** Establishes a WebSocket connection with the backend (`pilot`) to stream the conversation with the agent.
*   **Voice Input:** Captures audio input from the user and sends it to the backend for processing.
*   **Protected Routes:** Ensures that only authenticated users can access the co-pilot interface.

## Getting Started

### Prerequisites

*   Node.js and npm
*   Firebase Project

### Installation

1.  **Install dependencies:**
    ```bash
    npm install
    ```

2.  **Set Environment Variables:**
    Create a `.env.local` file and add your Firebase project configuration.

### Running Locally

```bash
npm run dev
```