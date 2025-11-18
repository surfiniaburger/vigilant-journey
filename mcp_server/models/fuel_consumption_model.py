import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import numpy as np

def train_fuel_consumption_model(data):
    """
    Trains a model to predict fuel consumption per lap.

    Args:
        data (pd.DataFrame): DataFrame containing telemetry data.
                             It must include 'nmot', 'ath', and 'fuel_consumption'.

    Returns:
        A trained machine learning model.
    """
    # Feature Engineering
    features = ['nmot', 'aps']
    target = 'fuel_consumption' # Assuming 'fuel_consumption' is the target variable

    X = data[features]
    y = data[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    # Evaluate the model
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    print(f"Fuel Consumption Model MSE: {mse}")

    return model

def predict_fuel_consumption(model, live_data):
    """
    Predicts the fuel consumption for a given lap.

    Args:
        model: The trained fuel consumption model.
        live_data (pd.DataFrame): A DataFrame with the live telemetry data.

    Returns:
        float: The predicted fuel consumption.
    """
    return model.predict(live_data)[0]
