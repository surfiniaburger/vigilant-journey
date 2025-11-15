import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import numpy as np

def train_tire_degradation_model(data):
    """
    Trains a model to predict tire degradation (lap time drop-off).

    Args:
        data (pd.DataFrame): DataFrame containing telemetry data.
                             It must include 'lap', 'accx_can', 'accy_can',
                             'Steering_Angle', and 'lap_time'.

    Returns:
        A trained machine learning model.
    """
    # Feature Engineering (simple example)
    features = ['lap', 'accx_can', 'accy_can', 'Steering_Angle']
    target = 'lap_time' # Assuming 'lap_time' is the target variable

    X = data[features]
    y = data[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    # Evaluate the model
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    print(f"Tire Degradation Model MSE: {mse}")

    return model

def predict_lap_time_dropoff(model, live_data):
    """
    Predicts the lap time drop-off based on live data.

    Args:
        model: The trained tire degradation model.
        live_data (pd.DataFrame): A DataFrame with the live telemetry data.

    Returns:
        float: The predicted lap time drop-off.
    """
    return model.predict(live_data)[0]
