import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import numpy as np

def train_pace_prediction_model(data):
    """
    Trains a model to predict the car's pace relative to competitors.

    Args:
        data (pd.DataFrame): DataFrame containing telemetry data. It must include
                             'Speed', 'Gear', 'nmot', 'ath', 'pbrake_f', 'pbrake_r',
                             'accx_can', 'accy_can', 'Steering_Angle', 'traffic',
                             and 'relative_pace'.

    Returns:
        A trained machine learning model.
    """
    # Feature Engineering
    features = ['speed', 'gear', 'nmot', 'aps', 'pbrake_f', 'pbrake_r',
                'accx_can', 'accy_can', 'Steering_Angle', 'traffic']
    target = 'relative_pace' # Assuming 'relative_pace' is the target variable

    X = data[features]
    y = data[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate the model
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    print(f"Pace Prediction Model MSE: {mse}")

    return model

def predict_pace(model, live_data):
    """
    Predicts the car's pace based on live data.

    Args:
        model: The trained pace prediction model.
        live_data (pd.DataFrame): A DataFrame with the live telemetry data.

    Returns:
        float: The predicted pace.
    """
    return model.predict(live_data)[0]
