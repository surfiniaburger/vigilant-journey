import logging
import os
from google.adk.agents import Agent
from pydantic import BaseModel, Field

# Configuration
INTERNAL_MODEL = os.getenv("INTERNAL_MODEL", "gemini-2.5-flash")

# --- Schemas ---

class TelemetryData(BaseModel):
    """Schema for incoming vehicle telemetry data."""
    speed_mph: float = Field(description="Current vehicle speed in miles per hour.")
    engine_temp_c: float = Field(description="Engine coolant temperature in Celsius.")
    fuel_level_percent: float = Field(description="Remaining fuel level as a percentage.")
    tire_pressure_psi: dict[str, float] = Field(
        description="Tire pressure in PSI for all four tires (FL, FR, RL, RR)."
    )
    error_codes: list[str] = Field(default_factory=list, description="Active vehicle diagnostic error codes.")

# --- Agent Definition ---

def create_telemetry_agent(callbacks=None):
    """
    Factory function to create the TelemetryAgent.
    The agent specializes in interpreting TelemetryData and providing performance summaries.
    """
    instruction = (
        "You are the Alora Telemetry Specialist. Your job is to analyze vehicle performance logs.\n"
        "1.  **Analyze**: Review the speed, engine temperature, fuel level, and tire pressures.\n"
        "2.  **Diagnose**: Interpret any error codes and relate them to the telemetry data.\n"
        "3.  **Advise**: Provide a concise summary of vehicle health and actionable recommendations (e.g., 'Pull over for cooling' or 'Tire pressure low').\n"
        "4.  **Tone**: Be professional, alert, and helpful."
    )
    
    return Agent(
        name="TelemetryAgent",
        model=INTERNAL_MODEL,
        instruction=instruction,
        output_key="telemetry_summary",
        **(callbacks or {})
    )

if __name__ == "__main__":
    # For quick debugging
    logging.basicConfig(level=logging.INFO)
    agent = create_telemetry_agent()
    print(f"Created TelemetryAgent with model: {agent.model}")
