
# Bitcoin Block Data Ingestion Pipeline

A **modern, async-first pipeline** to fetch Bitcoin block data from a full node, serialize in Avro, publish to Kafka, and archive into HDFS for Big Data analytics. This project leverages Fast Kafka, Avro serialization, async I/O, scalable consumer/producer patterns, and robust logging/observability for production-ready blockchain ingestion.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
    - [Clone the Repo](#clone-the-repo)
    - [Python Environment](#python-environment)
    - [Install Dependencies](#install-dependencies)
    - [Configuration](#configuration)
    - [External Services](#external-services)
        - [Bitcoin Full Node](#bitcoin-full-node)
        - [Kafka and Schema Registry](#kafka-and-schema-registry)
        - [Hadoop/HDFS](#hadoophdfs)
- [Avro Schemas](#avro-schemas)
- [Running the Pipeline](#running-the-pipeline)
    - [Producer](#producer)
    - [Consumer](#consumer)
- [Testing](#testing)
- [Logging \& Observability](#logging--observability)
- [DevOps \& Deployment](#devops--deployment)
- [Extending the System](#extending-the-system)
- [Design Recommendations](#design-recommendations)
- [FAQ / Troubleshooting](#faq--troubleshooting)
---

## Features

- **Async RPC** to Bitcoin full node for scalable data fetch.
- **Kafka Avro pipeline:** high-throughput, schema-enforced block ingestion.
- **Pluggable consumers:** easily extend to downstream ML/data jobs.
- **HDFS integration:** block data archived for Big Data/AI use-cases.
- **12-Factor App** ready: easy configuration, logging, and containerization.
- **Highly testable:** supports unit/integration testing and local development.


## Architecture

```
[Bitcoin Node] --> [Producer: Async Block Fetcher + Avro Encoder] --> [Kafka/Schema Registry] 
   --> [Consumer: Avro Decoder] --> [HDFS/Hadoop Storage]
```

- **Producer**: Async Python service fetches blocks (by height or time) via RPC, produces Avro records to Kafka.
- **Consumer**: Kafka Avro consumer deserializes, persists to HDFS.
- **Config-driven**: All connection details are managed by YAML/config classes.
- **Modular**: Utilities for logging, config, schema management.


## Prerequisites

- Python 3.8+
- Docker / docker-compose (recommended for running dependencies)
- Kafka, Schema Registry
- Hadoop/HDFS (WebHDFS)
- Running Bitcoin Core full node (with RPC enabled)
- [Optional] VirtualEnv, Conda, or Poetry for Python environment isolation


## Setup

### Clone the Repo

```bash
https://github.com/vikas-yadav-neo/Data-lake-with-Hadoop-and-S3
cd Data-lake-with-Hadoop-and-S3
cd bitcoin-hadoop-pipeline
```


### Python Environment

It's highly recommended to use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Or use poetry/micromamba as per your standards.

### Install Dependencies

```bash
pip install -r requirements.txt
```

The following extra Python packages are required and are present in `requirements.txt`:

- `aiohttp`
- `confluent-kafka[avro]`
- `hdfs`
- `PyYAML`
- `python-dotenv`
- Type hints: `mypy` (for linting), `black` (formatting), `flake8`


### Configuration

Configure everything via the YAML config loader (`src/utils/config_loader.py` expects a `config.yaml`).

**template for `src/utils/config.yaml`:**

```yaml
rpc:
  user: <rpc-username>
  password: <rpc-password>
  host: <bitcoin-node-host>
  port: 8332
  url: http://<bitcoin-node-host>:8332/
zmq:
  port: 28332
logging:
  json_file: logs/pipeline.json
  poll_interval: 10
  log_dir: logs/
postgres:
  host: localhost
  port: 5432
  name: blocks
  user: postgres
  password: password
wallet:
  addresses: []
electrum:
  host: <electrum-host>
  port: 50002
  use_ssl: false
  retry_delay: 3
kafka:
  host: localhost
  port: 9092
  bootstrap.servers: localhost:9092
  security.protocol: PLAINTEXT
  acks: all
  topics:
    raw-blocks: raw-blocks
schema-registry:
  host: localhost
  port: 8081
hadoop:
  url: http://localhost:9870
  user: neosoft
mongo:
  url: mongodb://localhost:27017
  database: blocks
influx:
  token: <influx-token>
```


### External Services

#### Bitcoin Full Node

- Run a synced Bitcoin node with RPC enabled.
- Set `rpcuser` and `rpcpassword` in your `bitcoin.conf`.


#### Kafka \& Schema Registry

- Easiest: use `confluentinc/cp-all-in-one` docker-compose (see below).
- Create topic(s) matching your config.
- Schema Registry must be enabled for Avro serialization.

**Sample docker-compose (Kafka + Schema Registry):**

```yaml
version: '2'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on: [zookeeper]
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    ports: ["9092:9092"]
  schema-registry:
    image: confluentinc/cp-schema-registry:latest
    depends_on: [kafka]
    environment:
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: PLAINTEXT://kafka:9092
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
      SCHEMA_REGISTRY_LISTENERS: http://0.0.0.0:8081
    ports: ["8081:8081"]
```


#### Hadoop/HDFS

- Install Hadoop locally or use Dockerized WebHDFS.
- Test connectivity: `hdfs dfs -ls /` or via WebHDFS API.


## Avro Schemas

- Place Avro schema files (`.avsc`) in the `schemas/` directory.
- Update the schema as needed for the block data structure.


## Running the Pipeline

### Producer

**Runs async block production (fetches Bitcoin blocks and pushes to Kafka, Avro-encoded).**

```bash
python src/producer/main.py
```

- You can change production parameters (block height range, topic name, etc.) in `src/producer/main.py` or via function arguments.
- By default, block heights are hardcoded, but you can use timestamp-based production as well (`produce_by_time_range`).


### Consumer

**Starts block consumer, reads Kafka topic, writes to HDFS.**

```bash
python src/consumer/main.py
```

- The consumer creates HDFS directories automatically.
- Each block is written as a JSON to `/user/neosoft/practice/data/bronze/blocks/` with the naming pattern: `block_<height>.json`.


## Testing

- Use `pytest` or `unittest` for core module testing.
- Mock Kafka, Bitcoin Core, and HDFS clients for integration testing.
- Use pre-commit hooks for linting/formatting:
`flake8`, `black`, `mypy` for type checks.


## Logging \& Observability

- Logs are written both to console and rotating files (`logs/`).
- Each service (producer, consumer) has its own log file and logger name.
- For production: integrate with ELK stack, Prometheus, or Grafana for real-time monitoring.


## DevOps \& Deployment

- **Containerization:** Use Docker for both services and dependencies (bitcoin, kafka, schema registry, hadoop).
- **Orchestration:** For scale, use Kubernetes (with StatefulSets for Kafka/HDFS).
- **CI/CD:** Integrate code quality steps and unit/integration test workflow (e.g., via GitHub Actions).
- **Secrets:** Use environment variables or tooling like HashiCorp Vault for sensitive data.
- **Production Readiness:** Add health-probes, graceful shutdowns, and automated config validation.


## FAQ / Troubleshooting

- **Message not appearing in Kafka?**
    - Check topic creation, Avro schema compatibility, and Kafka logs.
- **Can't connect to Bitcoin RPC?**
    - Validate `bitcoin.conf` and container networking configuration.
- **HDFS errors?**
    - Check WebHDFS endpoint and ensure permissions are correct.
- **Schema registry errors?**
    - Confirm registry is up and accessible, and that your schema file is valid.
- **Logging not writing to file?**
    - Ensure the `logs/` directory exists and is writable.

For more details or architecture discussions, raise an issue or start a GitHub discussion.
**PRs and suggestions are always welcome!**


