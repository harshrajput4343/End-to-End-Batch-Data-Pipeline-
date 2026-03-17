# Project Understanding & Implementation Details (AWS Stack)

## 📖 Overview
This project is a **Production-Grade Batch Data Pipeline** designed using the **AWS Modern Data Architecture**. It demonstrates the lifecycle of data using industry-standard tools like Airflow, S3, Redshift, and dbt.

---

## 🛠 Tech Stack Deep Dive

### 1. **Apache Airflow (Orchestration)**
*   **Why:** Orchestrates the multi-stage pipeline across S3, Redshift, and dbt.
*   **Where:** Triggers ingestion, S3 uploads, and Redshift COPY commands.

### 2. **Amazon S3 (Storage & Data Lake)**
*   **Why:** S3 is the backbone of AWS data pipelines. It provides 99.999999999% durability and acts as the staging area before data enters the warehouse.
*   **Where:** Stores the cleaned CSV files produced by the Python ETL script.

### 3. **Amazon Redshift (Data Warehouse)**
*   **Why:** A fully managed, petabyte-scale data warehouse. It uses columnar storage to provide blazing fast analytics.
*   **Where:** The final destination for our data, where complex SQL queries and dbt models are executed.

### 4. **dbt - Data Build Tool (Transformation)**
*   **Why:** Manages the transformation logic inside Redshift using modular SQL.
*   **Where:** Creates staging views and analytics tables directly in the Redshift cluster.

---

## 🎓 Interviewer Q&A (Top 15 - AWS Edition)

1.  **Q: Why use the Redshift `COPY` command instead of `INSERT`?**
    *   **A:** `COPY` is the optimized method for loading data from S3 to Redshift. It uses parallel processing to load data across all compute nodes, whereas `INSERT` is slow and processed by the leader node.
2.  **Q: What is the role of an IAM Role in this pipeline?**
    *   **A:** The Redshift cluster requires an IAM Role with permissions to read from S3. This role is passed in the `COPY` command to authorize the data transfer securely.
3.  **Q: How does Redshift differ from a traditional RDS database?**
    *   **A:** RDS is OLTP (Row-based), while Redshift is OLAP (Columnar). Redshift is optimized for large-scale aggregations and complex analytical queries rather than individual transaction updates.
4.  **Q: Why do we clean data in Python before moving it to S3?**
    *   **A:** This reduces the "noise" in our Data Lake. By handling nulls and types early, we ensure that the `COPY` command into Redshift is less likely to fail due to schema mismatches.
5.  **Q: What are Sort Keys and Dist Keys in Redshift?**
    *   **A:** **Sort Keys** determine the order data is stored on disk (like an index). **Dist Keys** determine how data is distributed across nodes. Both are critical for query performance at scale.
6.  **Q: How do you handle idempotency with S3?**
    *   **A:** By using predictable S3 keys (e.g., `year/month/day/file.csv`) and configuring the Redshift load to truncate or replace the target partition.
7.  **Q: Could we use AWS Glue instead of Python for ingestion?**
    *   **A:** Yes. Glue is a serverless ETL service that would handle this naturally. Python scripts were used here to provide more granular control and demonstrate local processing logic.
8.  **Q: What is MWAA?**
    *   **A:** Amazon Managed Workflows for Apache Airflow. It is the AWS-managed version of the Airflow environment used in this project.
9.  **Q: Why use dbt with Redshift?**
    *   **A:** dbt brings modularity and testing to Redshift SQL, allowing us to build a lineage graph and ensuring our analytic tables are accurate.
10. **Q: How do you secure data in transit to S3?**
    *   **A:** Boto3 uses HTTPS by default, and we can enforce S3 Bucket Policies that only allow encrypted (SSE-S3 or SSE-KMS) uploads.
11. **Q: What happens if the Redshift cluster is paused?**
    *   **A:** The Airflow DAG will fail at the `load_to_aws_task`. We can add a pre-task in Airflow to check the cluster status using the Redshift API.
12. **Q: How would you handle PII (Personally Identifiable Information) in this stack?**
    *   **A:** I would mask or hash the `user_id` in the Python `ingest.py` script before the data ever leaves the local environment for S3.
13. **Q: What is the "Leader Node" in Redshift?**
    *   **A:** It handles client connections, parses SQL, and coordinates parallel execution across the "Compute Nodes."
14. **Q: Why are Redshift staging models usually views?**
    *   **A:** Since staging usually just renames or casts data without aggregating, using a view avoids duplicating the storage cost of the raw load.
15. **Q: How do you monitor S3 costs?**
    *   **A:** By implementing S3 Lifecycle Policies to move older cleaned files to "Infrequent Access" or "Glacier" storage tiers.
