from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import os

# S3 credentials (MinIO)
os.environ["AWS_ACCESS_KEY_ID"] = "minioadmin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "minioadmin"

spark = SparkSession.builder \
    .appName("ETL-From-S3-to-Postgres") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Read raw data from MinIO (S3)
df = spark.read.json("s3a://rawdata/users.json")

# Simple transformation
df_transformed = df.select(
    col("id").alias("user_id"),
    col("name"),
    col("username"),
    col("email"),
    col("address.city").alias("city"),
    col("company.name").alias("company")
)

# Show output
df_transformed.show()

# Write to PostgreSQL
df_transformed.write \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://localhost:5434/sparkdemo") \
    .option("dbtable", "public.users") \
    .option("user", "postgres") \
    .option("password", "password") \
    .option("driver", "org.postgresql.Driver") \
    .mode("overwrite") \
    .save()

print("ETL complete: Data written to PostgreSQL.")