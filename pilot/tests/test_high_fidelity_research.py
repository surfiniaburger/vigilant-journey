import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from google.adk.agents.invocation_context import InvocationContext
from google_search_agent.agent import EscalationChecker, Feedback
from google.adk.events import Event

class MockContext:
    def __init__(self, state=None):
        self.session = MagicMock()
        self.session.state = state or {}
        self.plugin_manager = MagicMock()
        self.plugin_manager.run_before_agent_callback = AsyncMock(return_value=None)
        self.plugin_manager.run_after_agent_callback = AsyncMock(return_value=None)
        self.end_invocation = False
    def model_copy(self, update=None): return self

@pytest.mark.asyncio
async def test_escalation_checker_pass():
    """Verify that EscalationChecker escalates when grade is 'pass'."""
    checker = EscalationChecker(name="EscalationChecker")
    mock_ctx = MockContext(state={"critique_grade": "pass"})
    
    events = []
    async for event in checker.run_async(mock_ctx):
        events.append(event)
    
    assert len(events) == 1
    assert events[0].actions is not None
    assert events[0].actions.escalate is True

@pytest.mark.asyncio
async def test_escalation_checker_fail():
    """Verify that EscalationChecker does NOT escalate when grade is 'fail'."""
    checker = EscalationChecker(name="EscalationChecker")
    mock_ctx = MockContext(state={"critique_grade": "fail"})
    
    events = []
    async for event in checker.run_async(mock_ctx):
        events.append(event)
    
    assert len(events) == 1
    assert events[0].actions is None or events[0].actions.escalate in (False, None)

@pytest.mark.asyncio
async def test_feedback_schema_parsing():
    """Verify that the Feedback schema works as expected."""
    data = {"grade": "pass", "comment": "Great work!"}
    fb = Feedback(**data)
    assert fb.grade == "pass"
    assert fb.comment == "Great work!"
    
    with pytest.raises(Exception):
        Feedback(grade="not_a_valid_grade", comment="Oops")
