## Data Lake?

A large, centralized storage that holds all types of data.

Stores everything as-is — logs, videos, images, CSVs, JSONs, etc.

Example: AWS S3, Azure Data Lake Storage Gen2, Google Cloud Storage

## Data Warehouse?

A system used for reporting and data analysis.

Stores structured data (cleaned, transformed) within relational tables.

Example: Amazon Redshift, Snowflake, BigQuery, Azure Synapse Analytics

## objects
Files/data stored in a bucket
Can be anything: CSVs, logs, images, backups, documents
Identified by a key (like a filepath inside the bucket)

Each object consists of:

Data	      The actual file/content (e.g., CSV, image, video, Parquet, etc.)
Key	      A unique identifier for the object within a bucket (like a file path/name)
Metadata	Additional data about the object (e.g., file type, creation date)
Version ID	If versioning is enabled, each version gets a unique ID

- Example: 
Storing a file sales.csv in s3://my-bucket/data/2025/ →
It becomes an object with:

    Key: data/2025/sales.csv

    Content: the CSV file

    Metadata: file size, content type (text/csv), etc.

## Buckets 

Top-level container for storing data (like folders)

Each S3 bucket name is globally unique

- Example: s3://company-data-bucket

##  Regions

AWS has regions like us-east-1, ap-south-1, etc.

You create buckets in a specific region

Data is replicated across multiple availability zones within that region for durability

- Why Region Matters:
To reduce latency, meet data residency requirements, and optimize cost.

####  Why Do Industries Prefer S3?

🔁 Scalability	Can store petabytes or more without provisioning
💰 Cost-effective	Pay only for what you use (storage & requests)
🧱 Durability (11 9s)	99.999999999% durability — automatically replicated across zones
🔐 Security	IAM roles, bucket policies, encryption (SSE/KMS), access logs
🔄 High Availability	Designed for 99.99% uptime across multiple AZs
🚀 Integration	Works seamlessly with Glue, Athena, Redshift, Databricks, ADF, EMR, etc.
🔍 Query in-place	Use Athena or Redshift Spectrum without moving data
🌎 Global Access	Access from anywhere using REST API, SDKs, CLI
🗃️ Object Lifecycle	Archive to Glacier or delete based on rules
🔄 Versioning	Keeps history of changes to objects

## Data Ingestion into S3

Batch ingestion: via tools like AWS Glue, ADF, Lambda

Streaming ingestion: via Kinesis Data Streams, Kafka, Firehose

ETL tools: Apache NiFi, Informatica, Talend

Manual uploads: CLI, SDK, console

### Security and Governance

IAM:	                      Who can access AWS resources (identity-based)
Bucket Policies:	          What actions are allowed on a bucket (resource-based)
Encryption:	                Secure data at rest and in transit
AWS Lake Formation:	    Fine-grained access control, data cataloging

###  Real-World Use Cases
Netflix - Stores video logs and recommendation models in S3

Airbnb - Event data stored in S3, processed via Spark

GE(General Electric) - Industrial IoT data lake for turbines/machines

Pfizer - Genomics data lake for research

### What is Databricks?

Databricks is a unified analytics platform built for big data processing, AI/ML, and collaborative data engineering — all on the cloud, powered by Apache Spark.

Databricks = Apache Spark + Notebooks + Cloud + ML + Collaboration

## How Databricks Uses S3 as a Data Lake (way-1)

df = spark.read.format("csv").option("header", "true").load("s3a://your-bucket-name/raw/customers.csv")

df_cleaned = df.filter("age > 18").withColumnRenamed("cust_name", "customer_name")

df_cleaned.write.mode("overwrite").parquet("s3a://your-bucket-name/curated/customers")

## way-2 (using- dbutils.fs) 

dbutils.fs.mount(
  source = "s3a://my-bucket",
  mount_point = "/mnt/mydata",
  extra_configs = {"fs.s3a.access.key": "XXX", "fs.s3a.secret.key": "YYY"}
)


friendly file paths like 
df = spark.read.csv("/mnt/your-bucket-name/sales.csv")

Browse S3 Data Like a Local Filesystem 
%fs ls /mnt/your-bucket-name/

## Using S3 as a Data Lake in Azure Data Factory (similar service of aws is -aws Glue)

Create Linked Service for Amazon S3(add aws accesskey id and secrete access key)
Create Dataset (add bucket)
Create Activity (add created Linked Service and Dataset)

#### versioning in AWS 
-Keeps all versions of a file — allows restores and backups
-can save same name of files with different versions
