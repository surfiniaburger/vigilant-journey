import os
import json
import joblib
import pandas as pd
from typing import List, Text

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

import tensorflow as tf
from tensorflow_transform.tf_metadata import schema_utils

from tfx import v1 as tfx
from tfx_bsl.public import tfxio

# --- Feature and Target Definitions ---

TIRE_FEATURES = ['lap', 'accx_can', 'accy_can', 'Steering_Angle']
FUEL_FEATURES = ['nmot', 'aps']
PACE_FEATURES = ['speed', 'gear', 'nmot', 'aps', 'pbrake_f', 'pbrake_r',
                 'accx_can', 'accy_can', 'Steering_Angle', 'traffic']

TIRE_TARGET = 'lap_time'
FUEL_TARGET = 'fuel_consumption'
PACE_TARGET = 'relative_pace'

ALL_FEATURES = list(set(TIRE_FEATURES + FUEL_FEATURES + PACE_FEATURES))
ALL_TARGETS = [TIRE_TARGET, FUEL_TARGET, PACE_TARGET]

METRICS_FILE = "evaluation_metrics.json"

# --- Data Loading and Conversion ---

def _input_fn(file_pattern: List[Text],
              data_accessor: tfx.components.DataAccessor,
              schema: tfx.proto.Schema,
              batch_size: int = 200) -> tf.data.Dataset:
    """Generates a dataset from TFX IO."""
    return data_accessor.tf_dataset_factory(
        file_pattern,
        tfxio.TensorFlowDatasetOptions(batch_size=batch_size, label_key=PACE_TARGET),
        schema=schema).repeat()

def _get_raw_feature_spec(schema):
    """Generates a raw feature spec from the schema."""
    return schema_utils.schema_as_feature_spec(schema).feature_spec

def _dataset_to_pandas(dataset: tf.data.Dataset, schema: tfx.proto.Schema) -> pd.DataFrame:
    """Converts a tf.data.Dataset to a pandas DataFrame."""
    raw_feature_spec = _get_raw_feature_spec(schema)
    parsed_features = []
    # Take a finite number of records for conversion
    for tf_example_record in dataset.take(1000):
        parsed_record = tf.io.parse_example(tf_example_record, raw_feature_spec)
        parsed_features.append({
            key: val.numpy().squeeze()
            for key, val in parsed_record.items()
        })
    return pd.DataFrame(parsed_features)

# --- Model Training and Evaluation Logic ---

def _train_and_evaluate_model(model, train_df: pd.DataFrame, eval_df: pd.DataFrame,
                              features: List[Text], target: Text, model_path: Text):
    """Helper function to train, evaluate, and save a scikit-learn model."""
    X_train = train_df[features]
    y_train = train_df[target]
    X_eval = eval_df[features]
    y_eval = eval_df[target]

    model.fit(X_train, y_train)
    predictions = model.predict(X_eval)
    mse = mean_squared_error(y_eval, predictions)
    print(f"Model for '{target}' MSE: {mse}")

    joblib.dump(model, model_path)
    print(f"Model for '{target}' saved to {model_path}")
    return mse

# --- TFX Trainer run_fn ---

def run_fn(fn_args: tfx.components.FnArgs):
    """Train the three models and evaluate them."""
    schema = tfx.utils.parse_pbtxt_file(fn_args.schema_path, tfx.proto.Schema())

    # 1. Load and convert train and eval data
    train_dataset = _input_fn(fn_args.train_files, fn_args.data_accessor, schema)
    eval_dataset = _input_fn(fn_args.eval_files, fn_args.data_accessor, schema)

    train_df = _dataset_to_pandas(train_dataset, schema)
    eval_df = _dataset_to_pandas(eval_dataset, schema)

    # Simple data imputation
    for col in ALL_FEATURES + ALL_TARGETS:
        if col not in train_df.columns:
            train_df[col] = 0.0
        if col not in eval_df.columns:
            eval_df[col] = 0.0
    train_df.fillna(0, inplace=True)
    eval_df.fillna(0, inplace=True)

    # 2. Define models
    tire_model = LinearRegression()
    fuel_model = LinearRegression()
    pace_model = RandomForestRegressor(n_estimators=100, random_state=42)

    # 3. Define paths for saved models
    tire_model_path = os.path.join(fn_args.serving_model_dir, "tire_degradation_model.pkl")
    fuel_model_path = os.path.join(fn_args.serving_model_dir, "fuel_consumption_model.pkl")
    pace_model_path = os.path.join(fn_args.serving_model_dir, "pace_prediction_model.pkl")

    # 4. Train and evaluate each model
    tire_mse = _train_and_evaluate_model(tire_model, train_df, eval_df, TIRE_FEATURES, TIRE_TARGET, tire_model_path)
    fuel_mse = _train_and_evaluate_model(fuel_model, train_df, eval_df, FUEL_FEATURES, FUEL_TARGET, fuel_model_path)
    pace_mse = _train_and_evaluate_model(pace_model, train_df, eval_df, PACE_FEATURES, PACE_TARGET, pace_model_path)

    # 5. Save evaluation metrics
    metrics = {
        'tire_degradation_model_mse': tire_mse,
        'fuel_consumption_model_mse': fuel_mse,
        'pace_prediction_model_mse': pace_mse
    }
    metrics_path = os.path.join(fn_args.serving_model_dir, METRICS_FILE)
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f)
    print(f"Evaluation metrics saved to {metrics_path}")
