# MCP Server: Monte Carlo Simulation with a TFX Pipeline

This directory contains the `mcp_server`, a tool for running Monte Carlo simulations for race strategy, now enhanced with a production-grade MLOps workflow using TensorFlow Extended (TFX).

## Overview

The server provides race strategy insights by running simulations based on models for tire degradation, fuel consumption, and race pace. The ML models are now managed by a TFX pipeline that automates the process of data preparation, training, evaluation, and deployment.

## Environment Setup

**IMPORTANT:** This project uses the `tfx` library, which currently requires **Python 3.11 or lower**. Please ensure you are using a compatible Python version to run the pipeline and tests.

1.  **Create a Virtual Environment:**
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    ```

2.  **Install Dependencies:**
    First, install TFX, Apache Beam, and other core dependencies:
    ```bash
    pip install "tfx>=1.15.0" "apache-beam[interactive]>=2.46.0" pytest
    ```
    Then, install the project-specific dependencies:
    ```bash
    pip install -e .
    ```

## MLOps Workflow

The ML model lifecycle is managed by a series of scripts that should be run in order.

### 1. Prepare Data

This script downloads the raw race data, processes it into a unified CSV file, and places it in the correct directory for the TFX pipeline to use.

```bash
python3 mcp_server/prepare_data.py
```

### 2. Run the TFX Pipeline

This script orchestrates the end-to-end ML workflow. It will ingest the prepared data, train the models, evaluate their performance, and (if they pass a quality threshold) deploy them to the serving directory.

```bash
python3 mcp_server/pipeline/pipeline.py
```

### 3. Visualize Model Performance

After the pipeline has run, you can generate a visual report of the model performance metrics. This script reads the latest `evaluation_metrics.json` and creates a bar chart saved as `evaluation_results.png` in the latest model's directory.

```bash
python3 mcp_server/visualize_metrics.py
```

### 4. Start the Server

Once the pipeline has successfully run and a model has been deployed, you can start the MCP server. The server will automatically load the latest blessed model from the pipeline.

```bash
python3 mcp_server/main.py
```

## Testing

To verify the correctness of the pipeline components, run the unit tests using `pytest`. Make sure you are in the compatible Python 3.11 environment with all dependencies installed.

```bash
pytest mcp_server/tests/
```
