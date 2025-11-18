import numpy as np
import pandas as pd
import joblib
import os

from models.tire_degradation_model import predict_lap_time_dropoff
from models.fuel_consumption_model import predict_fuel_consumption
from models.pace_prediction_model import predict_pace

SAFETY_CAR_TIME_LOSS_SECONDS = 30

class MonteCarloSimulation:
    def __init__(self, race_data, num_simulations=1000, model_dir="trained_models"):
        self.race_data = race_data
        self.num_simulations = num_simulations
        self.tire_model = joblib.load(os.path.join(model_dir, "tire_degradation_model.pkl"))
        self.fuel_model = joblib.load(os.path.join(model_dir, "fuel_consumption_model.pkl"))
        self.pace_model = joblib.load(os.path.join(model_dir, "pace_prediction_model.pkl"))

        # Calculate average driver inputs
        self.avg_driver_inputs = {
            'accx_can': self.race_data['accx_can'].mean(),
            'accy_can': self.race_data['accy_can'].mean(),
            'Steering_Angle': self.race_data['Steering_Angle'].mean(),
            'nmot': self.race_data['nmot'].mean(),
            'aps': self.race_data['aps'].mean(),
            'pbrake_f': self.race_data['pbrake_f'].mean(),
            'pbrake_r': self.race_data['pbrake_r'].mean(),
            'speed': self.race_data['speed'].mean(),
            'gear': self.race_data['gear'].mean(),
        }


    def simulate_lap(self, live_data):
        """Simulates a single lap of the race."""

        tire_features = ['lap', 'accx_can', 'accy_can', 'Steering_Angle']
        fuel_features = ['nmot', 'aps']
        pace_features = ['speed', 'gear', 'nmot', 'aps', 'pbrake_f', 'pbrake_r',
                         'accx_can', 'accy_can', 'Steering_Angle', 'traffic']

        lap_time = predict_lap_time_dropoff(self.tire_model, live_data[tire_features])
        fuel_consumed = predict_fuel_consumption(self.fuel_model, live_data[fuel_features])

        return lap_time, fuel_consumed

    def run_strategy_simulation(self, strategy, safety_car_lap=None):
        """
        Runs a full race simulation for a given pit stop strategy.

        Args:
            strategy (list): A list of lap numbers for pit stops.
            safety_car_lap (int): The lap on which a safety car is deployed.

        Returns:
            float: The total race time for the simulated strategy.
        """
        total_race_time = 0
        tire_wear = 0
        fuel_level = 100 # start with a full tank

        total_laps = self.race_data['total_laps'].iloc[0] if 'total_laps' in self.race_data else 60
        pit_stop_time = 25 # seconds

        for lap in range(1, total_laps + 1):
            if lap in strategy:
                # Pit stop
                total_race_time += pit_stop_time
                tire_wear = 0 # Fresh tires
                fuel_level = 100 # Refuel

            live_data = pd.DataFrame({
                'lap': [tire_wear], # Use tire_wear as the feature for the model
                'accx_can': [self.avg_driver_inputs['accx_can']],
                'accy_can': [self.avg_driver_inputs['accy_can']],
                'Steering_Angle': [self.avg_driver_inputs['Steering_Angle']],
                'nmot': [self.avg_driver_inputs['nmot']],
                'aps': [self.avg_driver_inputs['aps']],
                'pbrake_f': [self.avg_driver_inputs['pbrake_f']],
                'pbrake_r': [self.avg_driver_inputs['pbrake_r']],
                'speed': [self.avg_driver_inputs['speed']],
                'gear': [self.avg_driver_inputs['gear']],
                'traffic': [0] # Placeholder for traffic data
            })

            lap_time, fuel_consumed = self.simulate_lap(live_data)

            total_race_time += lap_time
            if safety_car_lap and lap == safety_car_lap and lap not in strategy:
                total_race_time += SAFETY_CAR_TIME_LOSS_SECONDS

            tire_wear += 1
            fuel_level -= fuel_consumed

            if fuel_level <= 0:
                # Ran out of fuel, this strategy is invalid
                return float('inf')

        return total_race_time

    def find_optimal_pit_window(self):
        """
        Uses Monte Carlo simulation to find the optimal pit stop strategy.
        """
        # For simplicity, we'll test a few pre-defined strategies.
        # A more advanced implementation would generate these dynamically.
        strategies = {
            "1-stop": [[28]],
            "2-stop": [[20, 40]],
            "3-stop": [[15, 30, 45]]
        }

        best_strategy = None
        best_time = float('inf')

        for name, pit_stops in strategies.items():
            simulation_times = []
            for _ in range(self.num_simulations):
                total_time = self.run_strategy_simulation(pit_stops[0])
                simulation_times.append(total_time)

            avg_time = np.mean(simulation_times)

            print(f"Strategy: {name}, Avg. Time: {avg_time:.2f}s")

            if avg_time < best_time:
                best_time = avg_time
                best_strategy = name

        return best_strategy, best_time

    def analyze_undercut_overcut(self, competitor_pit_lap):
        """
        Analyzes the outcome of undercutting or overcutting a competitor.
        """
        print("\n--- Undercut/Overcut Analysis ---")
        # Simulate pitting 1 lap before, on the same lap, and 1 lap after
        undercut_strategy = [competitor_pit_lap - 1]
        match_strategy = [competitor_pit_lap]
        overcut_strategy = [competitor_pit_lap + 1]

        undercut_time = np.mean([self.run_strategy_simulation(undercut_strategy) for _ in range(self.num_simulations)])
        match_time = np.mean([self.run_strategy_simulation(match_strategy) for _ in range(self.num_simulations)])
        overcut_time = np.mean([self.run_strategy_simulation(overcut_strategy) for _ in range(self.num_simulations)])

        print(f"Undercut (pit at lap {competitor_pit_lap - 1}): {undercut_time:.2f}s")
        print(f"Match (pit at lap {competitor_pit_lap}): {match_time:.2f}s")
        print(f"Overcut (pit at lap {competitor_pit_lap + 1}): {overcut_time:.2f}s")

        # Return the time difference compared to matching the competitor
        return {
            "undercut_diff": undercut_time - match_time,
            "overcut_diff": overcut_time - match_time
        }

    def react_to_safety_car(self, current_lap):
        """
        Simulates the outcome of pitting during a safety car period.
        """
        print(f"\n--- Safety Car at Lap {current_lap} ---")

        # Scenario 1: Pit now
        pit_now_strategy = [current_lap]

        # Scenario 2: Stay out (assume a 1-stop strategy, pitting later)
        stay_out_strategy = [35]

        # Simulate with adjusted lap times for the safety car period
        # (This is a simplified assumption)

        # Scenario 1: Pit now
        pit_now_time = np.mean([self.run_strategy_simulation(pit_now_strategy, safety_car_lap=current_lap) for _ in range(self.num_simulations)])


        # Scenario 2: Stay out
        stay_out_time = np.mean([self.run_strategy_simulation(stay_out_strategy, safety_car_lap=current_lap) for _ in range(self.num_simulations)])

        print(f"Pit Now: {pit_now_time:.2f}s")
        print(f"Stay Out: {stay_out_time:.2f}s")

        if pit_now_time < stay_out_time:
            print("Recommendation: PIT NOW")
        else:
            print("Recommendation: STAY OUT")

        return pit_now_time, stay_out_time
