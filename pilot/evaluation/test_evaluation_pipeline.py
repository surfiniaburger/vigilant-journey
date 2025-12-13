import pytest
import asyncio
import os
import sys

# Ensure imports work by adding the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from evaluation.benchmark_prompts import run_benchmark

@pytest.mark.asyncio
async def test_evaluation_pipeline():
    """
    Runs the agent evaluation pipeline and fails if any test case is incorrect.
    This integrates the evaluation into the CI/CD workflow.
    """
    print("Starting Evaluation Pipeline...")
    
    # Run the benchmark
    results = await run_benchmark()
    
    # Analyze results
    failed_cases = [r for r in results if not r['is_correct']]
    pass_rate = (len(results) - len(failed_cases)) / len(results) * 100 if results else 0
    
    print(f"\nEvaluation Complete. Pass Rate: {pass_rate:.2f}% ({len(results) - len(failed_cases)}/{len(results)})")
    
    # Fail the test if there are any failures
    # You can adjust this threshold (e.g., allow 90% pass rate) if needed
    if failed_cases:
        error_msg = f"Evaluation failed for {len(failed_cases)} cases:\n"
        for case in failed_cases:
            error_msg += f"- ID: {case['eval_id']}\n  Query: {case['user_query']}\n  Result: {case['similarity_score']:.4f} (Threshold: 0.75)\n"
        pytest.fail(error_msg)
    
    assert len(results) > 0, "No evaluation cases were run!"
