import os
import zipfile
import pandas as pd
from pilot.data_handling.data_loader import unzip_data
from pilot.data_handling.telemetry_parser import parse_telemetry

def test_unzip_data(tmp_path):
    """Tests that the unzip_data function correctly unzips a file."""
    # Create a dummy zip file
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("test.txt", "This is a test file.")

    # Unzip the file
    unzip_data(data_dir=str(tmp_path), output_dir=str(tmp_path / "unzipped"))

    # Check that the file was unzipped
    assert os.path.exists(str(tmp_path / "unzipped" / "test" / "test.txt"))

def test_parse_telemetry(tmp_path):
    """Tests that the telemetry_parser correctly merges and processes data."""
    # Create dummy telemetry and analysis CSV files
    telemetry_data = {
        'timestamp': [1000, 2000, 3000],
        'lap': [1, 1, 32768],
        'vehicle_id': ['A', 'A', 'A'],
        'telemetry_name': ['speed', 'aps', 'nmot'],
        'telemetry_value': [100, 50, 7000]
    }
    df_telemetry = pd.DataFrame(telemetry_data)
    df_telemetry.to_csv(tmp_path / "telemetry.csv", index=False)

    analysis_data = {
        'LAP_NUMBER': [1],
        'DRIVER_NUMBER': [1],
        'LAP_TIME': ['1:30.500']
    }
    df_analysis = pd.DataFrame(analysis_data)
    df_analysis.to_csv(tmp_path / "Test_Analysis.csv", index=False, sep=';')

    # Parse the data
    parsed_data = parse_telemetry(str(tmp_path))

    # Check that the data was parsed correctly
    assert parsed_data is not None
    assert 'lap_time' in parsed_data.columns
    assert 'fuel_consumption' in parsed_data.columns
    assert 'relative_pace' in parsed_data.columns
    assert parsed_data['lap_time'].iloc[0] == 90.5
    assert parsed_data['lap'].iloc[2] == 1 # Check that lap 32768 was corrected
