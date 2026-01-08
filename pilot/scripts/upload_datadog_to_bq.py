
import json
import os
import argparse
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

def upload_dashboard_to_bq(json_path, project_id, dataset_id, table_id):
    # Initialize BigQuery client
    client = bigquery.Client(project=project_id)

    # 1. Ensure dataset exists
    dataset_ref = client.dataset(dataset_id)
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {dataset_id} already exists.")
    except NotFound:
        print(f"Creating dataset {dataset_id}...")
        client.create_dataset(bigquery.Dataset(dataset_ref))

    # 2. Define Table Schema
    schema = [
        bigquery.SchemaField("dashboard_title", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("widget_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("widget_title", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("widget_type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("raw_definition", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("uploaded_at", "TIMESTAMP", mode="NULLABLE", default_value_expression="CURRENT_TIMESTAMP()"),
    ]

    table_ref = dataset_ref.table(table_id)
    try:
        table = client.get_table(table_ref)
        print(f"Table {table_id} already exists.")
    except NotFound:
        print(f"Creating table {table_id}...")
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)

    # 3. Load Data
    with open(json_path, 'r') as f:
        dashboard_data = json.load(f)

    title = dashboard_data.get('title', 'Unknown Dashboard')
    widgets = dashboard_data.get('widgets', [])

    rows_to_insert = []
    for widget in widgets:
        definition = widget.get('definition', {})
        rows_to_insert.append({
            "dashboard_title": title,
            "widget_id": str(widget.get('id', '')),
            "widget_title": definition.get('title', ''),
            "widget_type": definition.get('type', ''),
            "raw_definition": json.dumps(widget)
        })

    if rows_to_insert:
        print(f"Inserting {len(rows_to_insert)} rows into {dataset_id}.{table_id}...")
        errors = client.insert_rows_json(table, rows_to_insert)
        if not errors:
            print("New rows have been added.")
        else:
            print(f"Encountered errors while inserting rows: {errors}")
            exit(1)
    else:
        print("No widgets found to insert.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload Datadog Dashboard JSON to BigQuery")
    parser.add_argument("--file", required=True, help="Path to Datadog JSON file")
    parser.add_argument("--project", help="GCP Project ID")
    parser.add_argument("--dataset", default="alora_metrics", help="BigQuery Dataset ID")
    parser.add_argument("--table", default="datadog_dashboards", help="BigQuery Table ID")

    args = parser.parse_args()

    project = args.project or os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project:
        print("Error: No project ID found. Use --project or set GOOGLE_CLOUD_PROJECT env var.")
        exit(1)

    upload_dashboard_to_bq(args.file, project, args.dataset, args.table)
