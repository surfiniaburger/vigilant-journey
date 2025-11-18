import os
from typing import Text
from absl import logging

from tfx import v1 as tfx
from tfx.orchestration import pipeline
from tfx.orchestration.beam.beam_dag_runner import BeamDagRunner

# --- Pipeline Configuration ---

PIPELINE_NAME = "mcp-server-pipeline"
PIPELINE_ROOT = os.path.join('mcp_server', 'pipelines', PIPELINE_NAME)
DATA_ROOT = os.path.join('mcp_server', 'unzipped_data', 'barber-motorsports-park', 'barber')
MODULE_FILE = os.path.join('mcp_server', 'pipeline', 'module.py')
SERVING_MODEL_DIR = os.path.join('mcp_server', 'serving_model', PIPELINE_NAME)

METADATA_PATH = os.path.join('mcp_server', 'metadata', PIPELINE_NAME, 'metadata.db')

# --- Pipeline Definition ---

def create_pipeline(
    pipeline_name: Text,
    pipeline_root: Text,
    data_root: Text,
    module_file: Text,
    serving_model_dir: Text,
    metadata_path: Text,
) -> pipeline.Pipeline:
    """Creates a TFX pipeline."""

    # 1. Data Ingestion (ExampleGen)
    # For this example, we assume the telemetry data has been parsed into a CSV.
    # We will need to create a CSV from the parsed data.
    # For now, we will point to the directory, and assume a CSV file exists.
    output_config = tfx.proto.Output(
        split_config=tfx.proto.SplitConfig(splits=[
            tfx.proto.SplitConfig.Split(name='train', hash_buckets=4),
            tfx.proto.SplitConfig.Split(name='eval', hash_buckets=1)
        ])
    )
    example_gen = tfx.components.CsvExampleGen(
        input_base=data_root,
        output_config=output_config
    )

    # 2. Data Validation (StatisticsGen, SchemaGen, ExampleValidator)
    statistics_gen = tfx.components.StatisticsGen(
        examples=example_gen.outputs['examples']
    )

    schema_gen = tfx.components.SchemaGen(
        statistics=statistics_gen.outputs['statistics'],
        infer_feature_shape=False
    )

    # 3. Model Training (Trainer)
    trainer = tfx.components.Trainer(
        module_file=module_file,
        examples=example_gen.outputs['examples'],
        schema=schema_gen.outputs['schema'],
        # We don't need train_args or eval_args for this scikit-learn setup
        custom_executor_spec=tfx.extensions.google_cloud_ai_platform.ExecutorSpec(
            python_executor=tfx.components.trainer.executor.GenericExecutor
        )
    )

    # 4. Model Evaluation & Pushing (Pusher)
    # In a real-world scenario, an Evaluator component would be used here
    # to assess the model's quality before pushing. For this example, we will
    # unconditionally push the model.
    pusher = tfx.components.Pusher(
        model=trainer.outputs['model'],
        push_destination=tfx.proto.PushDestination(
            filesystem=tfx.proto.PushDestination.Filesystem(
                base_directory=serving_model_dir
            )
        )
    )

    components = [
        example_gen,
        statistics_gen,
        schema_gen,
        trainer,
        pusher,
    ]

    return pipeline.Pipeline(
        pipeline_name=pipeline_name,
        pipeline_root=pipeline_root,
        components=components,
        metadata_connection_config=tfx.orchestration.metadata.sqlite_metadata_connection_config(metadata_path),
        enable_cache=True,
    )

if __name__ == '__main__':
    logging.set_verbosity(logging.INFO)

    # To run this pipeline, you would typically use a TFX orchestrator like
    # Kubeflow or a local runner. The BeamDagRunner is for local execution.
    # For this example, we're just defining the pipeline. A separate script
    # will be needed to run it.
    print("Pipeline definition complete. To run, use an orchestrator or a custom run script.")

    # Example of how to run with BeamDagRunner:
    #
    # pipeline = create_pipeline(
    #     pipeline_name=PIPELINE_NAME,
    #     pipeline_root=PIPELINE_ROOT,
    #     data_root=DATA_ROOT,
    #     module_file=MODULE_FILE,
    #     serving_model_dir=SERVING_MODEL_DIR,
    #     metadata_path=METADATA_PATH,
    # )
    # BeamDagRunner().run(pipeline)
