import os
import pandas as pd

from data_handling.data_downloader import download_and_move_files
from data_handling.data_loader import unzip_data
from data_handling.telemetry_parser import parse_telemetry

def main():
    """
    Prepares the data for the TFX pipeline by downloading, unzipping,
    parsing, and saving it as a CSV file.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    unzipped_data_dir = os.path.join(script_dir, 'unzipped_data')
    csv_output_dir = os.path.join(unzipped_data_dir, 'barber-motorsports-park', 'barber')

    # 1. Download and unzip data if not already present
    if not os.path.exists(data_dir):
        print("Downloading data...")
        download_and_move_files(data_dir)
    else:
        print("Data directory already exists.")

    if not os.path.exists(unzipped_data_dir):
        print("Unzipping data...")
        unzip_data(data_dir, unzipped_data_dir)
    else:
        print("Unzipped data directory already exists.")

    # 2. Parse the race data
    print("Parsing telemetry data...")
    race_data = parse_telemetry(csv_output_dir)

    if race_data is not None:
        # 3. Save the parsed data to a CSV file
        csv_output_path = os.path.join(csv_output_dir, 'data.csv')
        print(f"Saving parsed data to {csv_output_path}...")
        race_data.to_csv(csv_output_path, index=False)
        print("Data preparation complete.")
    else:
        print("Failed to parse race data. Data preparation failed.")

if __name__ == "__main__":
    main()
