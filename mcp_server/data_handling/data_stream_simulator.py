import pandas as pd
import time
import os
from pilot.data_handling.telemetry_parser import parse_telemetry

def stream_simulator(race_data_dir, delay_multiplier=1.0):
    """
    Simulates a real-time data stream from a telemetry CSV file.

    Args:
        race_data_dir (str): The path to the directory containing the race data.
        delay_multiplier (float): A factor to speed up or slow down the simulation.

    Yields:
        dict: A dictionary representing a single row of telemetry data.
    """
    # Find the main telemetry file (assuming it's the largest CSV)
    csv_files = [f for f in os.listdir(race_data_dir) if f.endswith('.csv')]
    if not csv_files:
        print(f"No CSV files found in {race_data_dir}")
        return

    main_telemetry_file = max(csv_files, key=lambda f: os.path.getsize(os.path.join(race_data_dir, f)))
    file_path = os.path.join(race_data_dir, main_telemetry_file)

    print(f"Streaming data from {file_path}...")
    df = parse_telemetry(file_path)

    if df is None:
        return

    # Assuming 'timestamp' is in milliseconds and represents the ECU time.
    # We calculate the time difference between consecutive timestamps to simulate the delay.
    if 'timestamp' in df.columns:
        df = df.sort_values(by='timestamp').reset_index(drop=True)
        df['time_diff'] = df['timestamp'].diff().fillna(0) / 1000.0  # Convert to seconds
    else:
        # If no timestamp, use a fixed delay
        df['time_diff'] = 0.1

    for index, row in df.iterrows():
        delay = row['time_diff'] * delay_multiplier
        time.sleep(delay)
        yield row.to_dict()
