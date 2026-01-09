import logging
import os
from typing import List, Optional
from google.adk.agents import Agent
from pydantic import BaseModel, Field

# Configuration
INTERNAL_MODEL = os.getenv("INTERNAL_MODEL", "gemini-2.5-flash")

# --- Schemas ---

class ExtractedEntity(BaseModel):
    """A specific data point found in a document."""
    label: str = Field(description="The name of the parameter (e.g., 'Cylinder Pressure', 'Torque Spec').")
    value: str = Field(description="The value of the parameter.")
    confidence: float = Field(description="Confidence in extraction (0.0 - 1.0).")

class IngestionSummary(BaseModel):
    """Structured result of the ingestion process."""
    document_type: str = Field(
        description="Categorization of the input. One of: [SERVICE_MANUAL, TELEMETRY_LOG, SITUATIONAL_VISION, USER_QUERY]"
    )
    entities: List[ExtractedEntity] = Field(default_factory=list, description="Key data points extracted from the input.")
    narrative_summary: str = Field(
        description="A concise technical summary for Alora's reasoning engine."
    )
    recommended_action: str = Field(
        description="Immediate recommendation based on the data (e.g., 'Check brake fluid', 'Compare with historical lap')."
    )

# --- Agent Definition ---

def create_ingestion_agent(callbacks=None):
    """
    Factory function for the IngestionAgent.
    This agent acts as a multi-modal triage layer, standardizing inputs (PDFs, CSVs, Images)
    into a structured text context for the main Intelligence Center.
    """
    instruction = (
        "You are the Alora Ingestion Gateway. Your role is to Triage complex multi-modal inputs.\n"
        "1.  **Classify**: Identify the type of data provided (e.g., is it a service manual PDF, a telemetry CSV, or a visual scene?).\n"
        "2.  **Extract**: Identify key technical entities (pressures, temperatures, torque specs, part numbers).\n"
        "3.  **Synthesize**: Provide a high-fidelity narrative summary that Alora can use to answer questions.\n"
        "4.  **Hardware Context**:\n"
        "    - If it's a SERVICE_MANUAL (Expert Mechanic story), focus on precise specs.\n"
        "    - If it's SITUATIONAL_VISION (Track Driver story), focus on immediate hazards or part identification.\n"
        "    - If it's TELEMETRY_LOG (Analyst story), focus on anomalies in sequences.\n"
        "Your output must be a single JSON object matching the IngestionSummary schema."
    )
    
    return Agent(
        name="IngestionAgent",
        model=INTERNAL_MODEL,
        instruction=instruction,
        output_schema=IngestionSummary,
        output_key="ingestion_context",
        **(callbacks or {})
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = create_ingestion_agent()
    print(f"Created IngestionAgent with model: {agent.model}")
