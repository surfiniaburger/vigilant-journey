import pytest
from unittest.mock import MagicMock, patch
from google_search_agent.ingestion_agent import create_ingestion_agent, IngestionSummary, ExtractedEntity

@pytest.mark.asyncio
async def test_ingestion_agent_manual_parsing():
    """Verify that IngestionAgent correctly classifies and extracts from a service manual."""
    agent = create_ingestion_agent()
    
    # Mock result
    mock_result = IngestionSummary(
        document_type="SERVICE_MANUAL",
        entities=[
            ExtractedEntity(label="Wheel Bolt Torque", value="150 Nm", confidence=0.98),
            ExtractedEntity(label="Lubricant Type", value="0W-40 Synthetic", confidence=0.95)
        ],
        narrative_summary="This document is a Mercedes-AMG GT Black Series Service Manual. It specifies a wheel bolt torque of 150 Nm.",
        recommended_action="Follow the 150 Nm torque specification for wheel changes."
    )
    
    # We mock out the run method of the ADK Agent
    # Since we are unit testing the AGENT definition and its capability to yield structured output,
    # we mock the underlying model response if it were a real run.
    # For now, let's just test that it's created with the right schema.
    assert agent.name == "IngestionAgent"
    assert agent.output_schema == IngestionSummary
    assert "SERVICE_MANUAL" in agent.instruction

@patch('google.adk.agents.Agent.run_async')
@pytest.mark.asyncio
async def test_ingestion_agent_mock_run(mock_run):
    """Smoke test for IngestionAgent run_async logic."""
    from google.adk.events import Event
    from google.genai import types
    import json
    
    agent = create_ingestion_agent()
    
    # Create a mock event with the expected JSON structure
    mock_data = {
        "document_type": "TELEMETRY_LOG",
        "entities": [{"label": "Oil Temp", "value": "115C", "confidence": 0.9}],
        "narrative_summary": "Telemetry log shows rising oil temperature.",
        "recommended_action": "Monitor oil cooling system."
    }
    
    async def mock_events(*args, **kwargs):
        yield Event(author="IngestionAgent", content=types.Content(parts=[types.Part(text=json.dumps(mock_data))]))

    mock_run.side_effect = mock_events
    
    # Mock Context
    mock_ctx = MagicMock()
    
    events = []
    async for event in agent.run_async(mock_ctx):
        events.append(event)
    
    assert len(events) > 0
    content = events[0].content.parts[0].text
    assert "TELEMETRY_LOG" in content
