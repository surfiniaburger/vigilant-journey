import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# Add current directory to path so we can import main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import main

def visualize_simulation_results():
    print("Initializing simulation...")
    if not main.initialize_simulation():
        print("Failed to initialize simulation. Cannot visualize.")
        return

    mc_sim = main.mc_simulation
    
    strategies = {
        "1-stop": [28],
        "2-stop": [20, 40],
        "3-stop": [15, 30, 45]
    }

    strategy_names = []
    avg_times = []

    print("Running simulations...")
    for name, pit_stops in strategies.items():
        print(f"Simulating {name} strategy...")
        simulation_times = []
        # Run fewer simulations for visualization speed
        for _ in range(100): 
            total_time = mc_sim.run_strategy_simulation(pit_stops)
            simulation_times.append(total_time)
        
        avg_time = np.mean(simulation_times)
        strategy_names.append(name)
        avg_times.append(avg_time)
        print(f"{name}: {avg_time:.2f}s")

    # Plotting
    print("Generating plot...")
    plt.figure(figsize=(10, 6))
    bars = plt.bar(strategy_names, avg_times, color=['skyblue', 'salmon', 'lightgreen'])
    
    # Add labels
    plt.ylabel('Average Race Time (seconds)')
    plt.title('Pit Stop Strategy Comparison (Monte Carlo Simulation)')
    plt.ylim(min(avg_times) * 0.99, max(avg_times) * 1.01) # Zoom in on the differences
    
    # Add values on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.1f}s', va='bottom', ha='center')

    output_file = "simulation_results.png"
    plt.savefig(output_file)
    print(f"Visualization saved to {output_file}")

if __name__ == "__main__":
    visualize_simulation_results()
