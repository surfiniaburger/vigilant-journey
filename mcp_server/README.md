# MCP Server: Monte Carlo Simulation with a TFX Pipeline

## Project Goal
This directory contains the `mcp_server`, a backend service designed for the "Hack the Track" hackathon. Its primary purpose is to provide real-time race strategy insights by running thousands of Monte Carlo simulations. The core of the server is a set of machine learning models that predict tire degradation, fuel consumption, and race pace.

To ensure the system is reliable, reproducible, and easy for others to run, the ML models are managed by a production-grade **MLOps workflow** built with TensorFlow Extended (TFX). This pipeline automates the entire process of data handling, model training, evaluation, and deployment.

---

## Environment Setup

**:warning: IMPORTANT:** This project uses the `tfx` library, which currently requires **Python 3.11 or lower**. Please ensure you create a virtual environment with a compatible Python version to run the pipeline and tests.

1.  **Create a Virtual Environment:**
    ```bash
    # Ensure you are using python3.11 or older
    python3.11 -m venv venv
    source venv/bin/activate
    ```

2.  **Install Dependencies:**
    First, install TFX, Apache Beam, and other core dependencies for the pipeline and visualization:
    ```bash
    pip install "tfx>=1.15.0" "apache-beam[interactive]>=2.46.0" pytest matplotlib
    ```
    Then, install the project-specific dependencies from `pyproject.toml`:
    ```bash
    pip install -e .
    ```

---

## MLOps Workflow: From Data to Deployed Model

The ML model lifecycle is managed by a series of scripts that should be run in the following order.

### 1. Prepare Data
**Command:** `python3 mcp_server/prepare_data.py`

This script is the entry point to the pipeline. It handles the initial data engineering tasks:
- **Downloads** the raw race telemetry data from the source.
- **Unzips and processes** the raw data.
- **Parses and cleans** the telemetry, merging it into a single, unified CSV file.
- **Output:** Creates a `data.csv` file inside `mcp_server/unzipped_data/barber-motorsports-park/barber/`, which is the input for the TFX pipeline.

### 2. Run the TFX Pipeline
**Command:** `python3 mcp_server/pipeline/pipeline.py`

This is the core of the MLOps workflow. It orchestrates the end-to-end ML process:
- **Data Ingestion & Validation:** Ingests the `data.csv`, splits it into training and evaluation sets, and generates statistics to validate the data.
- **Model Training:** Trains the three scikit-learn models (Tire, Fuel, Pace) using the training data.
- **Model Evaluation:** Evaluates the trained models against the evaluation dataset, calculating the Mean Squared Error (MSE) for each.
- **Model Blessing:** Compares the models' performance to a predefined quality threshold. If they pass, the model is "blessed" for deployment.
- **Model Deployment:** The blessed model and its associated metrics are pushed to a versioned directory in `mcp_server/serving_model/`.

### 3. Visualize Model Performance
**Command:** `python3 mcp_server/visualize_metrics.py`

After a model has been successfully trained and evaluated, this script provides a visual report of its performance.
- **Reads** the `evaluation_metrics.json` file from the latest blessed model's directory.
- **Generates** a bar chart comparing the MSE of the three models.
- **Output:** Saves the chart as `evaluation_results.png` in the same directory as the model, providing a clear, shareable view of the model's quality.

### 4. Start the Server
**Command:** `python3 mcp_server/main.py`

Once a model has been deployed by the pipeline, the server can be started.
- The server automatically finds and loads the **latest blessed model** from the `serving_model` directory.
- It exposes a single tool, `find_optimal_pit_window`, via the MCP protocol for the mobile app to consume.

---

## Key Components

-   `main.py`: The entry point for the MCP server application.
-   `monte_carlo_simulation.py`: Contains the core logic for running the race simulations.
-   `pipeline/`: The heart of the MLOps workflow.
    -   `pipeline.py`: Defines and orchestrates the TFX pipeline components.
    -   `module.py`: Contains the model training and evaluation logic (the `run_fn` for the TFX Trainer).
    -   `evaluator.py`: The custom component that blesses or rejects the model based on its performance.
-   `data_handling/`: Scripts for downloading and parsing the raw telemetry data.
-   `serving_model/`: The output directory where blessed, production-ready models are stored.
-   `tests/`: Unit tests for the data preparation and training modules.

---

## Testing

To verify the correctness of the pipeline's core logic, you can run the unit tests using `pytest`. Ensure you are in the correct Python 3.11 environment with all dependencies installed.

```bash
pytest mcp_server/tests/
```
