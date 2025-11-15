import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from pilot.models.tire_degradation_model import train_tire_degradation_model
from pilot.models.fuel_consumption_model import train_fuel_consumption_model
from pilot.models.pace_prediction_model import train_pace_prediction_model

def test_train_tire_degradation_model():
    """Tests that the tire degradation model trains and has a positive coefficient for the lap feature."""
    data = {
        'lap': np.arange(1, 51),
        'accx_can': np.random.rand(50),
        'accy_can': np.random.rand(50),
        'Steering_Angle': np.random.rand(50),
        'lap_time': 90 + np.arange(1, 51) * 0.1 # Simulate lap time increasing with laps
    }
    df = pd.DataFrame(data)
    model = train_tire_degradation_model(df)
    assert isinstance(model, LinearRegression)
    assert model.coef_[0] > 0 # The coefficient for the 'lap' feature should be positive

def test_train_fuel_consumption_model():
    """Tests that the fuel consumption model trains without errors."""
    data = {
        'nmot': np.random.rand(50),
        'aps': np.random.rand(50),
        'fuel_consumption': np.random.rand(50)
    }
    df = pd.DataFrame(data)
    model = train_fuel_consumption_model(df)
    assert isinstance(model, LinearRegression)

def test_train_pace_prediction_model():
    """Tests that the pace prediction model trains without errors."""
    data = {
        'speed': np.random.rand(50),
        'gear': np.random.rand(50),
        'nmot': np.random.rand(50),
        'aps': np.random.rand(50),
        'pbrake_f': np.random.rand(50),
        'pbrake_r': np.random.rand(50),
        'accx_can': np.random.rand(50),
        'accy_can': np.random.rand(50),
        'Steering_Angle': np.random.rand(50),
        'traffic': np.random.randint(0, 2, 50),
        'relative_pace': np.random.rand(50)
    }
    df = pd.DataFrame(data)
    model = train_pace_prediction_model(df)
    assert isinstance(model, RandomForestRegressor)
