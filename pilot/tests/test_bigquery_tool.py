import pytest
import asyncio
import os
import sys
from unittest.mock import MagicMock

# Add parent directory to path to allow importing from pilot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google_search_agent.bigquery_tool import query_vehicle_history
from google.adk.tools import ToolContext

@pytest.mark.asyncio
async def test_bigquery_history_lap_times():
    # 1. Setup Mock Context
    mock_tool_ctx = MagicMock()
    
    # 2. Run Tool for lap times
    result = await query_vehicle_history(mock_tool_ctx, "Tell me my lap times from last week")
    
    # 3. Assertions
    assert "avg_lap_time" in result
    assert "1:45.33" in result

@pytest.mark.asyncio
async def test_bigquery_history_top_speed():
    # 1. Setup Mock Context
    mock_tool_ctx = MagicMock()
    
    # 2. Run Tool for top speed
    result = await query_vehicle_history(mock_tool_ctx, "What was my highest speed?")
    
    # 3. Assertions
    assert "max_speed_mph" in result
    assert "158.4" in result

if __name__ == "__main__":
    asyncio.run(test_bigquery_history_lap_times())
    asyncio.run(test_bigquery_history_top_speed())
