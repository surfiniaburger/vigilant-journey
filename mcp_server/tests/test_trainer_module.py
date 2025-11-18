import os
import json
import joblib
import pytest
import tempfile
import pandas as pd
from unittest.mock import MagicMock

# Add the pipeline directory to the path to import the module
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pipeline')))

from module import run_fn

# --- Mock Objects to replace TFX dependencies ---

class MockFnArgs:
    """A mock class to simulate TFX's FnArgs."""
    def __init__(self, train_files, eval_files, schema_path, serving_model_dir, data_accessor):
        self.train_files = train_files
        self.eval_files = eval_files
        self.schema_path = schema_path
        self.serving_model_dir = serving_model_dir
        self.data_accessor = data_accessor

class MockDataAccessor:
    """A mock class to simulate the TFX DataAccessor."""
    def tf_dataset_factory(self, file_pattern, tfxio_options, schema):
        return []

# --- Test Fixtures ---

@pytest.fixture
def fn_args():
    """Creates a mock FnArgs object for testing the Trainer's run_fn."""
    with tempfile.TemporaryDirectory() as temp_dir:
        serving_model_dir = os.path.join(temp_dir, 'serving_model')
        os.makedirs(serving_model_dir, exist_ok=True)
        schema_path = os.path.join(temp_dir, 'schema.pbtxt')
        with open(schema_path, 'w') as f:
            f.write('')

        args = MockFnArgs(
            train_files=['train_dir'],
            eval_files=['eval_dir'],
            schema_path=schema_path,
            serving_model_dir=serving_model_dir,
            data_accessor=MockDataAccessor(),
        )
        yield args

# --- Tests ---

def test_run_fn_creates_models_and_metrics(fn_args, monkeypatch):
    """Tests that the run_fn trains and saves all models and the metrics file."""
    dummy_data = {
        'lap': [1, 2, 3], 'accx_can': [0.1, 0.2, 0.3], 'accy_can': [0.1, 0.2, 0.3],
        'Steering_Angle': [10, 15, 20], 'lap_time': [90, 91, 92],
        'nmot': [8000, 8100, 8200], 'aps': [50, 55, 60], 'fuel_consumption': [0.5, 0.55, 0.6],
        'speed': [150, 151, 152], 'gear': [4, 4, 5], 'pbrake_f': [0, 0, 1], 'pbrake_r': [0, 0, 0],
        'traffic': [0, 1, 0], 'relative_pace': [1.0, 1.1, 1.2]
    }
    dummy_df = pd.DataFrame(dummy_data)
    monkeypatch.setattr('module._dataset_to_pandas', lambda a, b: dummy_df)

    run_fn(fn_args)

    assert os.path.exists(os.path.join(fn_args.serving_model_dir, "tire_degradation_model.pkl"))
    assert os.path.exists(os.path.join(fn_args.serving_model_dir, "fuel_consumption_model.pkl"))
    assert os.path.exists(os.path.join(fn_args.serving_model_dir, "pace_prediction_model.pkl"))

    metrics_path = os.path.join(fn_args.serving_model_dir, "evaluation_metrics.json")
    assert os.path.exists(metrics_path)

    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
    assert 'tire_degradation_model_mse' in metrics
    assert 'fuel_consumption_model_mse' in metrics
    assert 'pace_prediction_model_mse' in metrics
