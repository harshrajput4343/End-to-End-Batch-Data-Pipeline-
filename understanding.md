# Project Understanding & Implementation Details (GCP Stack)

## 📖 Overview
This project is a **Production-Grade Batch Data Pipeline** designed using the **Google Cloud Modern Data Architecture**. It demonstrates the complete lifecycle of data — from raw ingestion to analytics-ready tables — using industry-standard tools like Apache Airflow, Google BigQuery, and dbt.

---

## 🛠 Tech Stack Deep Dive

### 1. **Apache Airflow (Orchestration)**
*   **Why:** Airflow is the industry standard for workflow management. Unlike simple Cron jobs or scripts, it provides complex dependency management, automatic retries, detailed monitoring via a rich UI, and a Python-native API.
*   **Where:** It sits at the top level, triggering each stage of the pipeline (`ingest` -> `load` -> `transform`).
*   **Key Concept:** **DAGs (Directed Acyclic Graphs)**. Our pipeline is a DAG where each node is a specific task that must complete before the next one begins.

### 2. **Google BigQuery (Data Warehouse)**
*   **Why:** BigQuery is a serverless, highly scalable cloud data warehouse. It allows us to store massive amounts of data and query it using standard SQL without managing infrastructure. You only pay for storage and queries, not for idle compute.
*   **Where:** It is our central data store. We use it for both the "Raw" (Bronze) layer and the "Analytics" (Gold) layer.
*   **Key Concept:** **Partitioning**. We partition our tables by date to ensure that queries are fast and cost-efficient by limiting the amount of data scanned.

### 3. **dbt - Data Build Tool (Transformation)**
*   **Why:** dbt allows data engineers to write modular SQL with software engineering best practices. It handles the "T" in ELT (Extract, Load, Transform), enabling version control, automated testing, and data lineage tracking.
*   **Where:** Once data is in BigQuery, dbt converts raw event logs into clean, aggregated tables ready for business intelligence tools.
*   **Key Concept:** **Materialization**. We use `views` for staging (saves storage, always fresh) and `tables` for analytics (faster query performance for dashboards).

### 4. **Python & Pandas (Ingestion/Cleaning)**
*   **Why:** Python is incredibly flexible for handling "dirty" raw data that doesn't fit standard SQL schemas yet. Pandas provides powerful row-level operations for null handling, type coercion, and date validation.
*   **Where:** Used in the `etl/ingest.py` script to clean raw CSV data before it enters the warehouse.

### 5. **Google Cloud SDK / `google-cloud-bigquery` (Cloud Integration)**
*   **Why:** The official Python client library provides seamless integration with BigQuery, including `LoadJob` configurations for partitioning, write disposition, and schema detection.
*   **Where:** Used in `etl/load_to_bq.py` to programmatically upload cleaned data.

---

## 🔄 Data Flow Process

1.  **Ingestion Phase**: A Python script reads `raw_events.csv`, cleans the data (removes rows with missing IDs, fixes date formats) and outputs `cleaned_events.csv`.
2.  **Loading Phase**: The cleaned CSV is loaded into BigQuery using the `google-cloud-bigquery` client library. The table is automatically partitioned by the event timestamp. `WRITE_TRUNCATE` disposition ensures idempotency.
3.  **Transformation Phase (dbt)**:
    *   **Staging (`stg_events`)**: dbt creates a **view** that renames columns and casts types into a standard format. This is the "cleaned" layer.
    *   **Analytics (`daily_event_counts`)**: dbt aggregates data (counts events and unique users per day, grouped by event type) and stores it in a **table** for fast BI tool access.

---

## 🎓 Interviewer Q&A (Top 15 - GCP Edition)

1.  **Q: Why use partitioning in BigQuery?**
    *   **A:** Partitioning limits the amount of data scanned during a query. Instead of reading the entire table, BigQuery only reads the relevant day's partition. This saves time and money (BigQuery charges per TB scanned).

2.  **Q: How do you handle transient failures in the pipeline?**
    *   **A:** I configured the Airflow DAG with `retries=2` and a `retry_delay=5min`. If a network glitch occurs during the BigQuery load, Airflow automatically retries before marking the task as failed.

3.  **Q: What is the benefit of an ELT approach over ETL?**
    *   **A:** By loading raw data first (EL) and then transforming it (T) inside BigQuery, we leverage its massive compute power rather than being limited by the memory and CPU of a single Python server.

4.  **Q: How do you ensure data quality?**
    *   **A:** I use dbt tests (defined in `sources.yml`) to check for nulls and unique constraints. If a test fails, the pipeline halts, and we know early that our source data is corrupted.

5.  **Q: Why dbt instead of BigQuery stored procedures?**
    *   **A:** dbt provides version control (Git), lineage tracking (dependency graphs via `ref()`), automated documentation, and testing. Stored procedures lack all of these engineering standards.

6.  **Q: What is an Idempotent Pipeline?**
    *   **A:** Running the same pipeline multiple times with the same input produces the same output. My `load_to_bq.py` uses `WRITE_TRUNCATE` which overwrites the table on each run, preventing duplicate records.

7.  **Q: How would you handle 10x more data?**
    *   **A:** BigQuery and Airflow both scale naturally. For dbt, I would switch to **Incremental materialization** so we only process new records instead of rebuilding the entire table.

8.  **Q: Why use the `BashOperator` instead of `PythonOperator`?**
    *   **A:** `BashOperator` decouples the Airflow worker environment from the Python/dbt execution environment. This prevents dependency conflicts and makes it easier to manage different tool versions.

9.  **Q: What is the difference between a View and a Table in BigQuery?**
    *   **A:** A **View** is a virtual table that re-runs the query every time it's accessed (saves storage, always fresh data). A **Table** stores actual data on disk (faster query performance, higher storage cost).

10. **Q: How do you manage GCP credentials securely?**
    *   **A:** I use a Service Account JSON key stored in an environment variable (`GCP_KEYFILE_PATH`). In production, I would use **GCP Secret Manager** or **Airflow Connections** to avoid storing keys on disk.

11. **Q: What happens if a dbt model fails?**
    *   **A:** Airflow detects the non-zero exit code from the `dbt run` CLI command, marks the `run_dbt_models_task` as failed, and halts all downstream tasks. Engineers are notified through Airflow's alerting system.

12. **Q: How do you track data lineage?**
    *   **A:** dbt automatically builds a lineage graph through the `ref()` and `source()` functions. You can view the entire data journey in the dbt documentation UI (`dbt docs generate && dbt docs serve`).

13. **Q: Why Pandas for cleaning instead of BigQuery SQL?**
    *   **A:** Pandas excels at row-level operations and schema inference when dealing with messy CSV files (invalid dates, missing fields). Trying to load corrupt CSVs directly into BigQuery would cause the `COPY` job to fail.

14. **Q: What is `catchup=False` in the Airflow DAG?**
    *   **A:** It prevents Airflow from executing "missed" DAG runs from the `start_date` to the current date when the DAG is first enabled. This is critical to prevent accidental massive data loads.

15. **Q: If you could add one more feature, what would it be?**
    *   **A:** I would add **Slack/Email Alerting** via Airflow's callback system (`on_failure_callback`) so engineers are notified immediately when any task in the pipeline fails.
