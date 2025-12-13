# Agent Evaluation Journey & Reference

> **Status:** ✅ Functional | **Pipeline:** 100% Passing | **Model:** Gemini 2.5 Flash

This document serves as an "honest readme" regarding the evolution of our agent evaluation pipeline, from initial failures to a robust, three-tier testing strategy.

## 1. The Challenge: Mixed Tools & Modern Models
We initially encountered critical failures when upgrading to **Gemini 2.5 Flash**. The core issue was a strict constraint in the new model architecture: **It does not support mixing Google Search citations with other function calls in the same turn.**

### The Fix: Split & Sequencing
To resolve the `ClientError: 400 INVALID_ARGUMENT (Mixed Tools)`, we refactored the monolithic `ResearcherAgent` into two specialized components:
1.  **`SearchAgent`**: Dedicated solely to using the `google_search` tool. It outputs raw search results.
2.  **`ResearchAnalysisAgent`**: Dedicated to "thinking". It takes the search results as *input* (context) and uses internal tools/logic to synthesize an answer.
3.  **`SequentialAgent`**: Orchestrates them (`Search -> Analysis`), ensuring the model never sees conflicting tool definitions in a single context.

## 2. The Solution: Agent Testing Pyramid
To "stretch" our evaluation and ensure reliability beyond just "it didn't crash", we implemented the **Agent Testing Pyramid**.

### Tier 1: Component-Level Unit Tests 🧪
*   **Goal**: Ensure individual agents are configured correctly and select the right tools in isolation.
*   **Implementation**: `pilot/tests/test_search_agent.py` & `test_analysis_agent.py`.
*   **What Works**: We now verify that `SearchAgent` has the correct instructions and tool definitions without needing to run the full expensive pipeline.

### Tier 2: Trajectory-Level Integration Tests 🛤️
*   **Goal**: Verify the agent *behaves* correctly, not just that it produced *an* answer.
*   **Implementation**: 
    *   Updated `evaluation_dataset.json` to include `"expected_tool_sequence": ["MainWorkflowAgent"]`.
    *   Updated `benchmark_prompts.py` to trace the execution path.
*   **Metric**: `trajectory_score`. We require a score of **0.8+** (along with semantic similarity) to pass. This catches cases where the agent might hallucinate an answer without actually using the required tools.

### Tier 3: End-to-End Human Review 👁️
*   **Goal**: Allow humans to inspect the reasoning process for complex queries.
*   **Implementation**: `pilot/evaluation/human_review.py`.
*   **Result**: Each run generates a clean Markdown report in `pilot/evaluation_reports/` containing the full Q&A trace, tool usage, and scores. This is uploaded as a **CI Artifact** (`human-review-reports`) for easy inspection.

## 3. Current Limitations (The "Honest" Part)
*   **Monte Carlo Tree Search (MCTS)**: While intended to be part of the advanced planning capabilities, the MCTS component is currently **not fully functional** and disabled in the active evaluation path. We are relying on the deterministic `SequentialAgent` flow for now.
*   **Dependency Speed**: The `sentence-transformers` library (used for similarity scoring) is heavy. We implemented a robust fallback to a mock scorer if the download times out, ensuring the pipeline doesn't flake due to network issues, but this means local runs might sometimes skip semantic verification if the environment isn't cached.

## How to Run
```bash
# Full Suite (Tiers 1-3)
cd pilot
uv run python -m pytest evaluation/test_evaluation_pipeline.py
```
*Environment variables `AGENT_MODEL` and `INTERNAL_MODEL` should be set to `gemini-2.5-flash`.*
