import os
import json
from tfx.dsl.component.experimental.decorators import component
from tfx.dsl.component.experimental.annotations import InputArtifact, OutputArtifact
from tfx.types.standard_artifacts import Model, ModelBlessing

# Define the path to the metrics file produced by the Trainer
METRICS_FILE = "evaluation_metrics.json"

# Define the quality threshold for the model
# In a real-world scenario, this would be more sophisticated.
MSE_THRESHOLD = 5.0 # Example threshold

@component
def CustomEvaluator(
    model: InputArtifact[Model],
    blessing: OutputArtifact[ModelBlessing]
):
    """
    A custom TFX component that evaluates the trained models and blesses them
    if they meet the quality threshold.
    """
    model_dir = model.uri
    metrics_path = os.path.join(model_dir, METRICS_FILE)

    if not os.path.exists(metrics_path):
        raise FileNotFoundError(f"Metrics file not found at {metrics_path}")

    with open(metrics_path, 'r') as f:
        metrics = json.load(f)

    # For this example, we'll check if the average MSE is below the threshold.
    avg_mse = sum(metrics.values()) / len(metrics)
    print(f"Average MSE: {avg_mse}")

    if avg_mse < MSE_THRESHOLD:
        print("Model passed quality threshold. Blessing model.")
        blessing.uri = os.path.join(model.uri, "blessed")
        blessing.set_int_custom_property("blessed", 1)
        # Create an empty file to signify the blessing
        with open(blessing.uri, "w") as f:
            f.write("")
    else:
        print("Model did not pass quality threshold. Not blessing model.")
        blessing.uri = os.path.join(model.uri, "not_blessed")
        blessing.set_int_custom_property("blessed", 0)
        # Create an empty file to signify the rejection
        with open(blessing.uri, "w") as f:
            f.write("")
