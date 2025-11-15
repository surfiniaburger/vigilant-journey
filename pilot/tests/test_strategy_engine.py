import pandas as pd
from unittest.mock import MagicMock
from pilot.strategy_engine.monte_carlo_simulation import MonteCarloSimulation

def setup_simulation(mocker):
    """Sets up a mocked MonteCarloSimulation object for testing."""
    mock_tire_model = MagicMock()
    mock_tire_model.predict.return_value = [90]
    mock_fuel_model = MagicMock()
    mock_fuel_model.predict.return_value = [1.5]
    mocker.patch('joblib.load', side_effect=[mock_tire_model, mock_fuel_model, MagicMock()])

    race_data = pd.DataFrame({
        'lap': range(1, 61),
        'accx_can': [0.5] * 60,
        'accy_can': [-0.2] * 60,
        'Steering_Angle': [15] * 60,
        'nmot': [7500] * 60,
        'aps': [80] * 60,
        'pbrake_f': [10] * 60,
        'pbrake_r': [5] * 60,
        'speed': [150] * 60,
        'gear': [4] * 60
    })
    race_data['total_laps'] = 60

    return MonteCarloSimulation(race_data, num_simulations=10)

def test_find_optimal_pit_window(mocker):
    """Tests the find_optimal_pit_window method."""
    mc_sim = setup_simulation(mocker)
    best_strategy, best_time = mc_sim.find_optimal_pit_window()
    assert best_strategy == "1-stop"
    assert best_time == 60 * 90 + 25

def test_react_to_safety_car(mocker):
    """Tests the react_to_safety_car method."""
    mc_sim = setup_simulation(mocker)
    pit_now_time, stay_out_time = mc_sim.react_to_safety_car(current_lap=25)
    assert pit_now_time < stay_out_time
