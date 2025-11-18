import pandas as pd
import os

def parse_telemetry(race_data_dir):
    """
    Parses telemetry data and merges it with lap times and other features.

    Args:
        race_data_dir (str): The path to the directory containing the race data.

    Returns:
        pandas.DataFrame: A cleaned and merged DataFrame with telemetry data.
    """
    try:
        # Find the main telemetry file (assuming it's the largest CSV)
        csv_files = [f for f in os.listdir(race_data_dir) if f.lower().endswith('.csv')]
        if not csv_files:
            print(f"No CSV files found in {race_data_dir}")
            return None

        main_telemetry_file = max(csv_files, key=lambda f: os.path.getsize(os.path.join(race_data_dir, f)))
        telemetry_file_path = os.path.join(race_data_dir, main_telemetry_file)

        # Find the analysis file
        analysis_file = [f for f in csv_files if 'Analysis' in f]
        if not analysis_file:
            print(f"Analysis file not found in {race_data_dir}")
            return None
        analysis_file_path = os.path.join(race_data_dir, analysis_file[0])

        # Read the analysis data
        df_analysis = pd.read_csv(analysis_file_path, delimiter=';')
        df_analysis.columns = df_analysis.columns.str.strip()

        # Rename columns in analysis data for merging
        df_analysis = df_analysis.rename(columns={'LAP_NUMBER': 'lap', 'DRIVER_NUMBER': 'driver_number', 'LAP_TIME': 'lap_time'})

        # Convert lap_time to seconds
        df_analysis['lap_time'] = df_analysis['lap_time'].apply(lambda x: sum(float(t) * 60**i for i, t in enumerate(reversed(str(x).split(':')))))

        # Create a lap time mapping
        lap_time_map = df_analysis.set_index('lap')['lap_time'].to_dict()

        # Process telemetry data in chunks
        df_telemetry_chunks = pd.read_csv(telemetry_file_path, chunksize=100000)

        processed_chunks = []
        for chunk in df_telemetry_chunks:
            # Handle the erroneous lap count in telemetry data
            if 'lap' in chunk.columns:
                chunk['lap'] = chunk['lap'].replace(32768, pd.NA).ffill()

            # Pivot the dataframe
            chunk = chunk.pivot_table(index=['timestamp', 'lap', 'vehicle_id'], columns='telemetry_name', values='telemetry_value').reset_index()

            # Map lap times
            chunk['lap_time'] = chunk['lap'].map(lap_time_map)
            processed_chunks.append(chunk)

        df_merged = pd.concat(processed_chunks)

        # Feature Engineering: Fuel Consumption Proxy
        # Normalize aps and nmot to a 0-1 scale
        df_merged['aps_norm'] = df_merged['aps'] / 100.0
        df_merged['nmot_norm'] = df_merged['nmot'] / df_merged['nmot'].max()
        df_merged['fuel_consumption'] = (0.7 * df_merged['aps_norm']) + (0.3 * df_merged['nmot_norm'])

        # Feature Engineering: Relative Pace
        fastest_laps = df_merged.groupby('lap')['lap_time'].min().reset_index()
        fastest_laps.rename(columns={'lap_time': 'fastest_lap'}, inplace=True)
        df_merged = pd.merge(df_merged, fastest_laps, on='lap', how='left')
        df_merged['relative_pace'] = df_merged['lap_time'] - df_merged['fastest_lap']

        return df_merged

    except FileNotFoundError:
        print(f"Error: A file was not found in {race_data_dir}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
