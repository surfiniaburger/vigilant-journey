import os
import json
import joblib
import pytest
import tempfile
import pandas as pd
from tfx.types import Artifact
from tfx.types.standard_artifacts import Model
from tfx.components.trainer.fn_args_utils import FnArgs
from unittest.mock import MagicMock

# Add the pipeline directory to the path to import the module
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pipeline')))

from module import run_fn

# A mock class to simulate the TFX DataAccessor
class MockDataAccessor:
    def tf_dataset_factory(self, file_pattern, tfxio_options, schema):
        # In a real test, you might want to create a mock TF Dataset.
        # For this test, since the module converts it to pandas anyway,
        # we can just return an empty list or a mock object.
        return []

@pytest.fixture
def fn_args():
    """Creates a mock FnArgs object for testing the Trainer's run_fn."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create dummy directories for inputs and outputs
        train_files_dir = os.path.join(temp_dir, 'train')
        eval_files_dir = os.path.join(temp_dir, 'eval')
        serving_model_dir = os.path.join(temp_dir, 'serving_model')
        os.makedirs(train_files_dir, exist_ok=True)
        os.makedirs(eval_files_dir, exist_ok=True)
        os.makedirs(serving_model_dir, exist_ok=True)

        # Create a dummy schema file (not used by the current module, but good practice)
        schema_path = os.path.join(temp_dir, 'schema.pbtxt')
        with open(schema_path, 'w') as f:
            f.write('')

        # Create mock data and save it as TFRecord files (or just mock the dataset)
        # For simplicity, we'll patch the _dataset_to_pandas function
        # to return a predefined DataFrame.

        # Create a mock Model artifact for the serving_model_dir
        serving_model_artifact = Model()
        serving_model_artifact.uri = serving_model_dir

        args = FnArgs(
            train_files=[train_files_dir],
            eval_files=[eval_files_dir],
            schema_path=schema_path,
            serving_model_dir=serving_model_dir,
            data_accessor=MockDataAccessor(),
        )
        yield args

def test_run_fn_creates_models_and_metrics(fn_args, monkeypatch):
    """Tests that the run_fn trains and saves all models and the metrics file."""
    # Create a dummy pandas DataFrame to be returned by the patched function
    dummy_data = {
        'lap': [1, 2, 3], 'accx_can': [0.1, 0.2, 0.3], 'accy_can': [0.1, 0.2, 0.3],
        'Steering_Angle': [10, 15, 20], 'lap_time': [90, 91, 92],
        'nmot': [8000, 8100, 8200], 'aps': [50, 55, 60], 'fuel_consumption': [0.5, 0.55, 0.6],
        'speed': [150, 151, 152], 'gear': [4, 4, 5], 'pbrake_f': [0, 0, 1], 'pbrake_r': [0, 0, 0],
        'traffic': [0, 1, 0], 'relative_pace': [1.0, 1.1, 1.2]
    }
    dummy_df = pd.DataFrame(dummy_data)

    # Use monkeypatch to replace _dataset_to_pandas with a function that returns our dummy df
    monkeypatch.setattr('module._dataset_to_pandas', lambda a, b: dummy_df)

    # Run the function
    run_fn(fn_args)

    # Check that the three model files were created
    assert os.path.exists(os.path.join(fn_args.serving_model_dir, "tire_degradation_model.pkl"))
    assert os.path.exists(os.path.join(fn_args.serving_model_dir, "fuel_consumption_model.pkl"))
    assert os.path.exists(os.path.join(fn_args.serving_model_dir, "pace_prediction_model.pkl"))

    # Check that the metrics file was created
    metrics_path = os.path.join(fn_args.serving_model_dir, "evaluation_metrics.json")
    assert os.path.exists(metrics_path)

    # Check the content of the metrics file
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
    assert 'tire_degradation_model_mse' in metrics
    assert 'fuel_consumption_model_mse' in metrics
    assert 'pace_prediction_model_mse' in metrics
