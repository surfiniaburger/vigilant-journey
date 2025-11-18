import os
import joblib
import pandas as pd
from typing import List, Text

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow_transform.tf_metadata import schema_utils

from tfx import v1 as tfx
from tfx_bsl.public import tfxio

# --- Feature and Target Definitions ---

# Define features for each model
TIRE_FEATURES = ['lap', 'accx_can', 'accy_can', 'Steering_Angle']
FUEL_FEATURES = ['nmot', 'aps']
PACE_FEATURES = ['speed', 'gear', 'nmot', 'aps', 'pbrake_f', 'pbrake_r',
                 'accx_can', 'accy_can', 'Steering_Angle', 'traffic']

# Define target for each model
TIRE_TARGET = 'lap_time'
FUEL_TARGET = 'fuel_consumption'
PACE_TARGET = 'relative_pace'

# All features used across the models
ALL_FEATURES = list(set(TIRE_FEATURES + FUEL_FEATURES + PACE_FEATURES))
ALL_TARGETS = [TIRE_TARGET, FUEL_TARGET, PACE_TARGET]

# --- Data Loading and Conversion ---

def _input_fn(file_pattern: List[Text],
              data_accessor: tfx.components.DataAccessor,
              schema: tfx.proto.Schema,
              batch_size: int = 200) -> tf.data.Dataset:
    """Generates a dataset from TFX IO."""
    return data_accessor.tf_dataset_factory(
        file_pattern,
        tfxio.TensorFlowDatasetOptions(
            batch_size=batch_size, label_key=PACE_TARGET), # A label key is required
        schema=schema).repeat()


def _get_raw_feature_spec(schema):
    """Generates a raw feature spec from the schema."""
    return schema_utils.schema_as_feature_spec(schema).feature_spec


def _dataset_to_pandas(dataset: tf.data.Dataset, schema: tfx.proto.Schema) -> pd.DataFrame:
    """Converts a tf.data.Dataset to a pandas DataFrame."""
    raw_feature_spec = _get_raw_feature_spec(schema)
    parsed_features = []
    for tf_example_record in dataset:
        parsed_record = tf.io.parse_example(tf_example_record, raw_feature_spec)
        # Squeeze tensors to scalars
        parsed_features.append({
            key: val.numpy().squeeze()
            for key, val in parsed_record.items()
        })
    return pd.DataFrame(parsed_features)


# --- Model Training Logic ---

def _train_and_save_model(model, data: pd.DataFrame, features: List[Text], target: Text, model_path: Text):
    """Helper function to train, evaluate, and save a scikit-learn model."""
    X = data[features]
    y = data[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model.fit(X_train, y_train)

    # Simple evaluation (optional, can be expanded)
    # predictions = model.predict(X_test)
    # mse = mean_squared_error(y_test, predictions)
    # print(f"Model for '{target}' MSE: {mse}")

    joblib.dump(model, model_path)
    print(f"Model for '{target}' saved to {model_path}")


# --- TFX Trainer run_fn ---

def run_fn(fn_args: tfx.components.FnArgs):
    """Train the three models based on the training data."""
    schema = tfx.utils.parse_pbtxt_file(fn_args.schema_path, tfx.proto.Schema())

    # 1. Load and convert data
    train_dataset = _input_fn(fn_args.train_files, fn_args.data_accessor, schema)
    # We need to load all data to train the different models, so we convert the whole dataset.
    # For large datasets, this should be done in a more memory-efficient way.
    train_df = _dataset_to_pandas(train_dataset, schema)

    # Ensure all necessary columns exist, fill NaNs if any
    for col in ALL_FEATURES + ALL_TARGETS:
        if col not in train_df.columns:
            # This is a simple fix for missing data. A real pipeline would need
            # a Transform component to handle this properly.
            train_df[col] = 0.0
    train_df.fillna(0, inplace=True)


    # 2. Define models
    tire_model = LinearRegression()
    fuel_model = LinearRegression()
    pace_model = RandomForestRegressor(n_estimators=100, random_state=42)

    # 3. Define paths for saved models
    tire_model_path = os.path.join(fn_args.serving_model_dir, "tire_degradation_model.pkl")
    fuel_model_path = os.path.join(fn_args.serving_model_dir, "fuel_consumption_model.pkl")
    pace_model_path = os.path.join(fn_args.serving_model_dir, "pace_prediction_model.pkl")

    # 4. Train and save each model
    _train_and_save_model(tire_model, train_df, TIRE_FEATURES, TIRE_TARGET, tire_model_path)
    _train_and_save_model(fuel_model, train_df, FUEL_FEATURES, FUEL_TARGET, fuel_model_path)
    _train_and_save_model(pace_model, train_df, PACE_FEATURES, PACE_TARGET, pace_model_path)
