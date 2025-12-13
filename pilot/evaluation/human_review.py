import json
import os
from datetime import datetime

def generate_human_review_report(results, output_dir="evaluation_reports"):
    """
    Generates a Markdown report for human review of the agent's performance.
    Tier 3 of the Agent Testing Pyramid.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(output_dir, f"human_review_{timestamp}.md")
    
    with open(report_file, "w") as f:
        f.write(f"# Agent Evaluation Human Review\n")
        f.write(f"**Date:** {datetime.now()}\n\n")
        
        pass_count = sum(1 for r in results if r['is_correct'])
        total = len(results)
        f.write(f"## Summary\n")
        f.write(f"- **Pass Rate:** {pass_count}/{total} ({(pass_count/total)*100:.1f}%)\n")
        f.write(f"- **Total Cases:** {total}\n\n")
        
        f.write("## Detailed Traces\n")
        for case in results:
            status = "✅ PASS" if case['is_correct'] else "❌ FAIL"
            f.write(f"### Case {case['eval_id']}: {status}\n")
            f.write(f"**User Query:** {case['user_query']}\n\n")
            f.write(f"**Expected Trajectory:** `{case.get('expected_tools', [])}`\n")
            f.write(f"**Actual Trajectory:** `{case.get('actual_tools', [])}`\n")
            f.write(f"**Trajectory Score:** {case.get('trajectory_score', 0.0):.2f}\n\n")
            
            f.write(f"**Reference Answer:**\n> {case['reference_answer']}\n\n")
            f.write(f"**Generated Answer:**\n> {case['generated_answer']}\n\n")
            f.write(f"**Similarity Score:** {case['similarity_score']:.4f}\n")
            f.write("---\n")
            
    return report_file
