import logging
import os
from google.adk.agents import Agent
from pydantic import BaseModel, Field

# Configuration
INTERNAL_MODEL = os.getenv("INTERNAL_MODEL", "gemini-2.5-flash")

# --- Schemas ---

class VisionAnalysis(BaseModel):
    """Structured description of visual content for downstream non-modal agents."""
    objects_detected: list[str] = Field(description="List of primary objects seen in the image.")
    colors_and_environment: str = Field(description="Summary of the environment, lighting, and dominant colors.")
    text_or_signs: str = Field(description="Transcription of any visible text, road signs, or console indicators.")
    safety_hazards: list[str] = Field(description="Potential hazards seen (e.g., 'smoke', 'cracked glass', 'obstruction').")
    overall_description: str = Field(description="A high-fidelity paragraph summarizing the scene for Alora's reasoning engine.")

# --- Agent Definition ---

def create_vision_agent(callbacks=None):
    """
    Factory function for the VisionAgent.
    This agent has vision and is responsible for 'translating' images into text descriptions.
    """
    instruction = (
        "You are the Alora Vision Specialist. You possess high-fidelity vision capabilities.\n"
        "Your goal is to describe the provided image in extreme detail for a blind reasoning agent.\n"
        "1.  **Analyze**: Look at objects, text, indicators, and environmental conditions.\n"
        "2.  **Safety**: Prioritize identifying any hazards (e.g., warning lights, smoke, obstacles).\n"
        "3.  **Translate**: Convert the visual data into a structured text summary that captures the essence of the scene.\n"
        "Your output must be a single JSON object matching the VisionAnalysis schema."
    )
    
    return Agent(
        name="VisionAgent",
        model=INTERNAL_MODEL,
        instruction=instruction,
        output_schema=VisionAnalysis,
        output_key="vision_summary",
        **(callbacks or {})
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = create_vision_agent()
    print(f"Created VisionAgent with model: {agent.model}")
