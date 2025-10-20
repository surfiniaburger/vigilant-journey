import sys
from unittest.mock import MagicMock

# Mock motor module to avoid ImportError in the test environment
# This will be executed by pytest before it collects tests.
sys.modules['motor'] = MagicMock()
sys.modules['motor.motor_asyncio'] = MagicMock()
