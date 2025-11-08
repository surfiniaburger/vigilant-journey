
import pytest
import json
from unittest.mock import MagicMock, patch, mock_open, AsyncMock

# Mock the sentence_transformers library before it's imported by the script
import sys

# Create a mock SentenceTransformer class with a mock encode method
mock_sentence_transformer = MagicMock()
mock_sentence_transformer.encode.return_value = MagicMock()
sys.modules['sentence_transformers'] = MagicMock(SentenceTransformer=MagicMock(return_value=mock_sentence_transformer))
from sentence_transformers import util

# This import must happen AFTER the mocks are set up
from pilot.evaluation import benchmark_prompts

@pytest.fixture
def mock_runner():
    """Provides a mock runner for testing."""
    runner = MagicMock()

    # Configure the async generator for run_async
    async def mock_run_async(*args, **kwargs):
        yield MagicMock(turn_complete=True, content=MagicMock(parts=[MagicMock(text="mocked answer")]))

    runner.run_async = mock_run_async
    runner.session_service = AsyncMock()
    runner.session_service.create_session = AsyncMock(return_value=MagicMock(id="test-session"))
    return runner

@pytest.fixture
def mock_file_data():
    """Provides mock data for the evaluation dataset."""
    return json.dumps({
        "eval_cases": [
            {
                "eval_id": "case001",
                "user_query": "What is the capital of France?",
                "reference_answer": "Paris"
            }
        ]
    })

@pytest.mark.asyncio
@patch('pilot.evaluation.benchmark_prompts.initialize_evaluation_services')
@patch('builtins.open', new_callable=mock_open)
@patch('pilot.evaluation.benchmark_prompts.util')
async def test_main_logic_success(mock_util, mock_open_file, mock_init_services, mock_runner, mock_file_data):
    """Tests the main evaluation script logic for a successful run."""
    # Arrange
    mock_init_services.return_value = mock_runner
    mock_open_file.return_value.read.return_value = mock_file_data
    mock_util.pytorch_cos_sim.return_value.item.return_value = 0.9  # High similarity score

    # Act
    await benchmark_prompts.main()

    # Assert
    mock_open_file.assert_called_with(benchmark_prompts.EVALUATION_DATASET_PATH, 'r')
    assert mock_init_services.called
    assert mock_runner.session_service.create_session.called
    assert mock_util.pytorch_cos_sim.called


@pytest.mark.asyncio
@patch('pilot.evaluation.benchmark_prompts.initialize_evaluation_services')
@patch('builtins.open', new_callable=mock_open)
@patch('pilot.evaluation.benchmark_prompts.util')
@patch('sys.exit')
async def test_main_logic_failure(mock_exit, mock_util, mock_open_file, mock_init_services, mock_runner, mock_file_data):
    """Tests the main evaluation script logic for a failure run."""
    # Arrange
    mock_init_services.return_value = mock_runner
    mock_open_file.return_value.read.return_value = mock_file_data
    mock_util.pytorch_cos_sim.return_value.item.return_value = 0.5  # Low similarity score

    # Act
    await benchmark_prompts.main()

    # Assert
    mock_exit.assert_called_with(1)
