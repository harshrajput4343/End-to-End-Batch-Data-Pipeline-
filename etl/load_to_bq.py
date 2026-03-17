from google.cloud import bigquery
import pandas as pd
import os

def load_to_bigquery(csv_path, table_id, project_id):
    """
    Loads a cleaned CSV file into a BigQuery table.
    Uses WRITE_TRUNCATE for idempotency (no duplicate loads on re-runs).
    Partitions by the 'timestamp' column for query performance and cost savings.
    """
    client = bigquery.Client(project=project_id)
    
    # Define job configuration
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        # Partitioning by the 'timestamp' column
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="timestamp",
        ),
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    with open(csv_path, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_id, job_config=job_config)

    job.result()  # Wait for the job to complete.

    table = client.get_table(table_id)
    print(f"Loaded {table.num_rows} rows to {table_id}.")

if __name__ == "__main__":
    PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-project-id")
    DATASET_ID = os.getenv("BQ_DATASET_RAW", "raw_data")
    TABLE_NAME = os.getenv("BQ_TABLE_EVENTS", "events")
    TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}"
    
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CSV_PATH = os.path.join(PROJECT_ROOT, 'data', 'cleaned_events.csv')
    
    if os.path.exists(CSV_PATH):
        print(f"Loading {CSV_PATH} to BigQuery table {TABLE_ID}...")
        # Uncomment the line below when GCP credentials are configured:
        # load_to_bigquery(CSV_PATH, TABLE_ID, PROJECT_ID)
        print("Bypassing actual upload (simulated for project template).")
    else:
        print(f"File {CSV_PATH} not found. Run ingest.py first.")
