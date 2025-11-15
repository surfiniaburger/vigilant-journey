import pandas as pd
import os
import joblib
from pilot.data_handling.telemetry_parser import parse_telemetry
from pilot.models.tire_degradation_model import train_tire_degradation_model
from pilot.models.fuel_consumption_model import train_fuel_consumption_model
from pilot.models.pace_prediction_model import train_pace_prediction_model

def train_and_save_models(race_data_dir, model_dir="trained_models"):
    """
    Trains all the predictive models and saves them to disk.

    Args:
        race_data_dir (str): The path to the directory containing the race data.
        model_dir (str): The directory to save the trained models to.
    """
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    # Parse the data
    data = parse_telemetry(race_data_dir)
    if data is None:
        print("Failed to parse data. Aborting training.")
        return

    # Drop rows with missing values
    data.dropna(inplace=True)

    # Train and save the tire degradation model
    print("Training Tire Degradation Model...")
    tire_model = train_tire_degradation_model(data)
    joblib.dump(tire_model, os.path.join(model_dir, "tire_degradation_model.pkl"))
    print("Tire Degradation Model saved.")

    # Train and save the fuel consumption model
    print("\nTraining Fuel Consumption Model...")
    fuel_model = train_fuel_consumption_model(data)
    joblib.dump(fuel_model, os.path.join(model_dir, "fuel_consumption_model.pkl"))
    print("Fuel Consumption Model saved.")

    # Train and save the pace prediction model
    print("\nTraining Pace Prediction Model...")
    # 'traffic' column might not exist, so we create a dummy one if it doesn't
    if 'traffic' not in data.columns:
        data['traffic'] = 0
    pace_model = train_pace_prediction_model(data)
    joblib.dump(pace_model, os.path.join(model_dir, "pace_prediction_model.pkl"))
    print("Pace Prediction Model saved.")

if __name__ == '__main__':
    # Use the barber motorsports park data for training
    race_dir = 'unzipped_data/barber-motorsports-park/barber'
    train_and_save_models(race_dir)
