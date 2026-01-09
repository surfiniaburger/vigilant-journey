import logging
import os
from typing import Literal
from google.adk.agents import Agent
from pydantic import BaseModel, Field

# Configuration
INTERNAL_MODEL = os.getenv("INTERNAL_MODEL", "gemini-2.5-flash")

# --- Schemas ---

class JudgeOutput(BaseModel):
    """Schema for the Judge's evaluation of telemetry analysis."""
    grade: Literal["pass", "fail"] = Field(
        description="Whether the telemetry summary meets safety standards. 'pass' if safe/normal, 'fail' if a SEV-1 or critical hazard is detected."
    )
    reasoning: str = Field(
        description="Detailed explanation for the grade, focusing on safety implications."
    )
    is_sev1: bool = Field(
        description="True if the situation constitutes a SEV-1 emergency (e.g., active fire, complete system failure, high-speed collision risk)."
    )

# --- Agent Definition ---

def create_judge_agent(callbacks=None):
    """
    Factory function to create the JudgeAgent.
    The agent acts as a quality gate (The Sieve) for telemetry summaries.
    """
    instruction = (
        "You are the Alora Safety Judge. Your job is to strictly evaluate telemetry summaries.\n"
        "1.  **Evaluate**: Review the 'telemetry_summary' in the session state.\n"
        "2.  **Sieve**: Determine if the reported conditions indicate a SEV-1 emergency or a safety hazard.\n"
        "3.  **Grade**: \n"
        "    - Assign 'fail' if you see high temperatures (>110C), critical fuel, low tire pressure at high speed, or critical engine error codes.\n"
        "    - Assign 'pass' only if the car is operating within safe parameters.\n"
        "4.  **SEV-1 Flag**: Explicitly set is_sev1 to True if immediate user intervention or emergency protocols are required.\n"
        "Your output must be a single JSON object matching the JudgeOutput schema."
    )
    
    return Agent(
        name="JudgeAgent",
        model=INTERNAL_MODEL,
        instruction=instruction,
        output_schema=JudgeOutput,
        output_key="judge_evaluation",
        disallow_transfer_to_peers=True, # The Judge only judges.
        **(callbacks or {})
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = create_judge_agent()
    print(f"Created JudgeAgent with model: {agent.model}")
