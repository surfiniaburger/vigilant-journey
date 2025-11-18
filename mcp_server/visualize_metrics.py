import os
import json
import glob
import matplotlib.pyplot as plt
import pandas as pd

from pipeline.pipeline import SERVING_MODEL_DIR

METRICS_FILE = "evaluation_metrics.json"
OUTPUT_IMAGE_FILE = "evaluation_results.png"

def find_latest_metrics_file():
    """Finds the latest evaluation_metrics.json file from the TFX pipeline output."""
    pushed_model_dirs = glob.glob(os.path.join(SERVING_MODEL_DIR, "*"))
    if not pushed_model_dirs:
        return None
    latest_model_dir = max(pushed_model_dirs, key=os.path.getmtime)
    metrics_path = os.path.join(latest_model_dir, METRICS_FILE)
    return metrics_path if os.path.exists(metrics_path) else None

def main():
    """
    Generates a bar chart from the latest model evaluation metrics and saves it as a PNG.
    """
    print("Generating visual analytics...")

    # 1. Find the latest metrics file
    metrics_path = find_latest_metrics_file()
    if not metrics_path:
        print(f"Error: No '{METRICS_FILE}' found in the serving directory: {SERVING_MODEL_DIR}")
        print("Please run the TFX pipeline first to produce a model and its metrics.")
        return

    print(f"Loading metrics from: {metrics_path}")

    # 2. Read the metrics data
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)

    # 3. Create a DataFrame for plotting
    metrics_df = pd.DataFrame(list(metrics.items()), columns=['Model', 'MSE'])
    # Clean up model names for the plot
    metrics_df['Model'] = metrics_df['Model'].str.replace('_model_mse', '').str.replace('_', ' ').str.title()


    # 4. Generate and save the plot
    plt.figure(figsize=(10, 6))
    bars = plt.bar(metrics_df['Model'], metrics_df['MSE'], color=['skyblue', 'salmon', 'lightgreen'])
    plt.ylabel('Mean Squared Error (MSE)')
    plt.title('Model Performance Evaluation')
    plt.xticks(rotation=15, ha="right")
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Add MSE values on top of the bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.4f}', va='bottom', ha='center')


    output_path = os.path.join(os.path.dirname(metrics_path), OUTPUT_IMAGE_FILE)
    plt.savefig(output_path)

    print(f"Visual analytics saved to: {output_path}")

if __name__ == "__main__":
    main()
