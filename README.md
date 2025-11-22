# Alora Racing Strategy: Real-Time AI Analytics

> **"How might we make the single best strategic decision in seconds, when a simple miscalculation will lose the race?"**

**Alora** is an AI-powered Race Strategy Optimization System designed to solve the race engineer's most pervasive problem: the battle against time and unpredictability.

## The Problem: Zero Tolerance for Error

In high-stakes motorsport (F1, IndyCar, NASCAR), the Race Strategist faces an overwhelming challenge. They must process gigabytes of telemetry data—tire degradation, fuel loads, weather patterns, competitor pace—in milliseconds.

*   **The Pain Point**: A human cannot simulate thousands of race strategies in seconds. When a safety car comes out or a sudden downpour begins, the "pre-race plan" is useless. The engineer is overwhelmed, and a single bad call costs millions in prize money and championship points.
*   **The Stakes**: The decision must be made now. There is no "undo" button.

## The Solution: AI-Driven Monte Carlo Simulation

Alora solves this by leveraging **Artificial Intelligence** to do what humans cannot: scale.

*   **Massive Scale**: Instead of guessing, Alora runs thousands of **Monte Carlo simulations** in real-time to find the statistically optimal path.
*   **Adaptation**: It adapts to adverse conditions (safety cars, traffic) instantly, providing a data-backed recommendation when the pressure is highest.
*   **Speed**: By parallelizing computations on the cloud, Alora delivers complex strategy analysis (1-stop vs. 2-stop vs. 3-stop) in ~2 minutes, transforming a 7-minute manual calculation into an interactive decision-making tool.

---

## System Architecture

The system consists of two main components:

### 1. The Backend (`mcp_server/`)
A **Model Context Protocol (MCP)** server built with Python and **FastMCP**, deployed on **Google Cloud Run**.
*   **Core Engine**: `monte_carlo_simulation.py` loads trained ML models (Tire Degradation, Fuel Consumption, Pace Prediction) from **Google Cloud Storage**.
*   **Infrastructure**:
    *   **Cloud Run**: Serverless, auto-scaling container execution.
    *   **Lazy Loading**: Models are loaded only on the first request to ensure instant server startup.
    *   **Parallel Execution**: The server supports concurrent requests, allowing the client to trigger multiple strategy simulations simultaneously.

### 2. The Client (`android_app/` - Mooncake Repo)
An Android application that serves as the race engineer's command center.
*   **Visualization**: A 3D map of Barber Motorsports Park (using Sceneform/OpenGL) visualizes car positions and strategy overlays.
*   **Real-Time Updates**: Connects to the backend via **Server-Sent Events (SSE)** to receive strategy updates as they are calculated.
*   **Heads-Up Display (HUD)**: Displays the optimal pit window and predicted race time for each strategy.

## Deployment & Setup

### Backend (Google Cloud Run)
The server is deployed to the `us-central1` region.

```bash
gcloud run deploy monte-carlo-mcp-server \
  --source . \
  --region us-central1 \
  --project gem-creator \
  --allow-unauthenticated \
  --set-env-vars GCS_BUCKET_NAME=monte-carlo-mcp-assets \
  --timeout=3600 \
  --cpu-boost \
  --no-cpu-throttling
```

### Android Client
The Android app is hosted in the `mooncake` submodule. It uses **GitHub Actions** for CI/CD to automatically build and release signed APKs.

## Key Technologies
*   **Python 3.11** & **uv** (Dependency Management)
*   **FastMCP** (Server Framework)
*   **Scikit-Learn** & **Pandas** (ML Models)
*   **Google Cloud Platform** (Run, Storage)
*   **Kotlin** & **OkHttp** (Android Client)
*   **Server-Sent Events (SSE)** (Real-time Communication)