import logging
import os
from typing import Annotated
from google.cloud import bigquery
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
DATASET_ID = "vigilant_journey"
TABLE_ID = "telemetry_history"

async def query_vehicle_history(
    ctx: ToolContext,
    query_description: Annotated[str, "A clear description of the historical data needed (e.g., 'What was my average lap time last week?')"]
) -> str:
    """
    Queries historical vehicle telemetry and performance data from BigQuery.
    Use this to answer questions about past sessions, trends, or comparisons.
    """
    if not PROJECT_ID:
        return "Error: GOOGLE_CLOUD_PROJECT environment variable not set."

    try:
        client = bigquery.Client(project=PROJECT_ID)
        
        # In a real implementation, we would use an LLM or logic to translate 
        # the query_description into SQL. For this bit, we demonstrate the tool's 
        # capability by providing a mock-sql-execution path.
        
        # Example SQL generation (Conceptual)
        # sql = f"SELECT AVG(lap_time) FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}` WHERE ..."
        
        # Mocking BQ response for the "Bit" phase
        if "lap time" in query_description.lower():
            results = [
                {"session_date": "2026-01-01", "avg_lap_time": "1:45.33"},
                {"session_date": "2026-01-02", "avg_lap_time": "1:44.89"},
                {"session_date": "2026-01-03", "avg_lap_time": "1:46.12"}
            ]
        elif "top speed" in query_description.lower() or "highest speed" in query_description.lower():
            results = [{"max_speed_mph": 158.4, "session_date": "2026-01-05"}]
        else:
            return "No historical records found matching that description. Try being more specific about the metric (e.g., lap time, temperature, speed)."

        # Format results
        formatted_results = "\n".join([str(r) for r in results])
        return f"Historical Data Results:\n{formatted_results}"

    except Exception as e:
        logger.error(f"BigQuery Query Error: {e}")
        return f"Error querying vehicle history: {str(e)}"

# Alias
bigquery_history_tool = query_vehicle_history
