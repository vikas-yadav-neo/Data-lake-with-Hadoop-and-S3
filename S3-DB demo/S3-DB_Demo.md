
## S3-DB Demo: README

### Overview

The **S3-DB demo** demonstrates an end-to-end ETL flow from a simulated S3-compatible object storage (MinIO) into a PostgreSQL database using PySpark. The workflow covers:

- Bootstrapping a local data lake environment (MinIO, PostgreSQL via Docker Compose).
- Ingesting sample JSON data to MinIO.
- Extracting, transforming, and loading (ETL) that data into a relational database via Spark.


### Table of Contents

- [Directory Structure](#directory-structure)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
    - [1. Start the Docker Services](#1-start-the-docker-services)
    - [2. Upload Data to MinIO](#2-upload-data-to-minio)
    - [3. Run Spark ETL to PostgreSQL](#3-run-spark-etl-to-postgresql)
- [Expected Data Flow](#expected-data-flow)
- [Troubleshooting \& Tips](#troubleshooting--tips)
- [Extending This Demo](#extending-this-demo)


### Directory Structure

```
S3-DB demo/
├── docker-compose.yml           # Docker Compose for MinIO & PostgreSQL
├── etl_s3_to_postgres.py        # PySpark ETL pipeline script
└── upload_data_to_minio.py      # Script: Demo data → S3 (MinIO)
```


### Prerequisites

- **Docker** (latest, includes Docker Compose)
- **Python 3.7+** for upload script
- **PySpark** (recommend using Spark 3.x, installable via pip)
- **boto3** and **requests** (for `upload_data_to_minio.py`)
- **Java** (needed for PySpark on most systems)
- **Spark JDBC** driver for PostgreSQL (see below)


### Setup Instructions

#### 1. Start the Docker Services

- Spin up MinIO (S3-compatible) and PostgreSQL locally:

```bash
cd 'S3-DB demo'
docker-compose up -d
```

- MinIO console: [http://localhost:9001](http://localhost:9001)
User: `minioadmin`, Password: `minioadmin`
- PostgreSQL exposed on `localhost:5434`
User: `postgres`, Password: `password`, Database: `sparkdemo`


#### 2. Upload Data to MinIO

- Install required Python packages if not already present:

```bash
pip install boto3 requests
```

- Run the data upload script:

```bash
python upload_data_to_minio.py
```

This script fetches sample user data and uploads it as **users.json** to a MinIO bucket named `rawdata`.

#### 3. Run Spark ETL to PostgreSQL

- Ensure Spark and PySpark are installed.
- Download the [PostgreSQL JDBC driver](https://jdbc.postgresql.org/download.html) and place it in your Spark classpath.
- Run the ETL job (update the driver path if needed):

```bash
spark-submit --jars /path/to/postgresql-<version>.jar etl_s3_to_postgres.py
```

Or, for standalone PySpark environments:

```bash
export PYSPARK_SUBMIT_ARGS="--jars /path/to/postgresql-<version>.jar pyspark-shell"
python etl_s3_to_postgres.py
```

- The ETL script reads user data from `s3a://rawdata/users.json`, transforms it, and loads it into the `public.users` table in PostgreSQL.


### Expected Data Flow

| Component | Description |
| :-- | :-- |
| **upload_data_to_minio** | Loads demo data into MinIO (`rawdata/users.json`) |
| **etl_s3_to_postgres** | Reads from S3, transforms, and loads into PostgreSQL |
| **PostgreSQL (db)** | Stores processed user data in relational format |

### Troubleshooting \& Tips

- **Unable to connect to MinIO or PostgreSQL?**
    - Check that services are running (`docker ps`)
    - Verify ports: MinIO (9000, 9001), PostgreSQL (5434)
- **Spark errors on S3 read?**
    - Ensure all S3-related `spark.hadoop.fs.s3a.*` configs match those in the script.
    - MinIO must be running before launching Spark job.
- **JDBC connection/driver issues?**
    - Place the correct PostgreSQL JDBC driver in the Spark classpath.


### Extending This Demo

- Substitute different public APIs for demo data.
- Add more transformation logic in `etl_s3_to_postgres.py`.
- Generalize upload/ETL for other entity types.
- Integrate with workflow orchestrators (e.g., Airflow, Prefect).

