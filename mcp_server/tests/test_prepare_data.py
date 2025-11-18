import os
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

# Since the prepare_data script is not in a package, we need to add its directory to the path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from prepare_data import main as prepare_data_main

@pytest.fixture
def temp_data_dir(tmp_path):
    """Creates a temporary data directory structure for testing."""
    mcp_server_dir = tmp_path / "mcp_server"
    data_dir = mcp_server_dir / "data"
    unzipped_dir = mcp_server_dir / "unzipped_data" / "barber-motorsports-park" / "barber"
    unzipped_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    # Create a dummy analysis and telemetry file
    analysis_data = {
        'LAP_NUMBER': [1], 'LAP_TIME': ['1:30.5'], 'DRIVER_NUMBER': [1]
    }
    telemetry_data = {
        'timestamp': [100], 'lap': [1], 'vehicle_id': [1],
        'telemetry_name': ['speed'], 'telemetry_value': [150]
    }
    pd.DataFrame(analysis_data).to_csv(unzipped_dir / "Test_Analysis.csv", index=False, sep=';')
    pd.DataFrame(telemetry_data).to_csv(unzipped_dir / "Test_Telemetry.csv", index=False)

    return mcp_server_dir


@patch('prepare_data.download_and_move_files')
@patch('prepare_data.unzip_data')
@patch('prepare_data.parse_telemetry')
def test_prepare_data_main(mock_parse_telemetry, mock_unzip_data, mock_download_files, temp_data_dir):
    """Tests the main data preparation script."""
    # Mock the functions that download and unzip data
    mock_download_files.return_value = None
    mock_unzip_data.return_value = None

    # Mock the telemetry parser to return a simple DataFrame
    mock_parsed_df = pd.DataFrame({'lap': [1], 'speed': [150]})
    mock_parse_telemetry.return_value = mock_parsed_df

    # We need to change the working directory so the script can find the data
    original_cwd = os.getcwd()
    os.chdir(temp_data_dir)

    # Run the script
    with patch('prepare_data.script_dir', '.'):
         prepare_data_main()


    # Check that the output CSV was created
    output_csv_path = "unzipped_data/barber-motorsports-park/barber/data.csv"
    assert os.path.exists(output_csv_path)

    # Check the content of the CSV
    result_df = pd.read_csv(output_csv_path)
    pd.testing.assert_frame_equal(result_df, mock_parsed_df)

    # Clean up
    os.chdir(original_cwd)
