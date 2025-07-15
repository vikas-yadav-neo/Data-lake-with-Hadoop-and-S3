import requests
import json
from io import BytesIO
import boto3

# Dummy API
url = "https://jsonplaceholder.typicode.com/users"
response = requests.get(url)
data = response.json()

# Connect to MinIO
s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin',
    region_name='us-east-1'
)

# Create bucket if not exists
bucket = "rawdata"
try:
    s3.head_bucket(Bucket=bucket)
except:
    s3.create_bucket(Bucket=bucket)

json_lines = "\n".join([json.dumps(record) for record in data])
json_bytes = BytesIO(json_lines.encode('utf-8'))

s3.upload_fileobj(json_bytes, bucket, "users.json")

print("Uploaded users.json to MinIO S3")