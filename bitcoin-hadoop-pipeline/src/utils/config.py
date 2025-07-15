import os
from dataclasses import dataclass, field
from dotenv import load_dotenv
from pathlib import Path
# from pymongo import MongoClient
# from pymongo.errors import ConnectionFailure
# from confluent_kafka import Consumer
# from confluent_kafka.admin import AdminClient, NewTopic
from utils.config_loader import loaded_config
from utils.logger import logger


@dataclass
class Config:


    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    SCHEMA_DIR: Path = BASE_DIR / "schemas"


    RPC_USER: str = loaded_config.rpc.user
    RPC_PASSWORD: str = loaded_config.rpc.password
    RPC_HOST: str = loaded_config.rpc.host
    RPC_PORT: int = loaded_config.rpc.port
    RPC_URL: str = loaded_config.rpc.url


    ZMQ_PORT: int = loaded_config.zmq.port


    LOG_JSON_FILE: str = loaded_config.logging.json_file


    POLL_INTERVAL: int = loaded_config.logging.poll_interval


    DB_HOST: str = loaded_config.database.host
    DB_PORT: int = loaded_config.database.port
    DB_NAME: str = loaded_config.database.name
    DB_USER: str = loaded_config.database.user
    DB_PASSWORD: str = loaded_config.database.password
    DB_DIALECT: str = "postgresql"


    ELECTRUM_HOST: str = loaded_config.electrum.host
    ELECTRUM_PORT: int = loaded_config.electrum.port
    USE_SSL: bool = loaded_config.electrum.use_ssl
    RETRY_DELAY: int = loaded_config.electrum.retry_delay


    KAFKA_HOST: str = loaded_config.kafka.host
    KAFKA_PORT: int = loaded_config.kafka.port
    KAFKA_BOOTSTRAP_SERVERS: str = f"{str(KAFKA_HOST)}:{str(KAFKA_PORT)}"
    KAFKA_SECURITY_PROTOCOL: str = loaded_config.kafka.security_protocol
    KAFKA_ACKS: str = loaded_config.kafka.acks
    KAFKA_TOPICS: dict = field(default_factory=lambda: loaded_config.kafka.topics)
    KAFKA_CONFIG: dict = field(default_factory=lambda: {
        "bootstrap.servers": loaded_config.kafka.bootstrap_servers,
        "security.protocol": loaded_config.kafka.security_protocol,
        "acks": loaded_config.kafka.acks,
    })

    SCHEMA_REGISTRY_HOST: str = loaded_config.schema_registry.host
    SCHEMA_REGISTRY_PORT: int = loaded_config.schema_registry.port
    SCHEMA_REGISTRY_URL: str = f"http://{SCHEMA_REGISTRY_HOST}:{str(SCHEMA_REGISTRY_PORT)}"


    HADOOP_URL: str = loaded_config.hadoop.url
    HADOOP_USER: str = loaded_config.hadoop.user
    HADOOP_PASSWORD: str = loaded_config.hadoop.password


    WALLET_ADDRESSES: list = field(default_factory=lambda: loaded_config.wallet.addresses)


    MONGO_URL: str = loaded_config.mongo.url
    MONGO_DATABASE: str = loaded_config.mongo.database


    INFLUX_TOKEN: str = loaded_config.influx.token


    LOG_DIR: str = loaded_config.logging.log_dir


    # BASE_DIR = Path.cwd()
    BLOCK_LOG_DIR = os.path.join(BASE_DIR, 'logs', 'block_logs')
    TX_LOG_DIR = os.path.join(BASE_DIR, 'logs', 'transaction_logs')

config = Config()

"""def ping_mongodb():
    try:
        mongo_client = MongoClient(config.MONGO_URL, serverSelectionTimeoutMS=5000)
        mongo_client.admin.command("ping")
        logger.info(f"✅ Successfully connected to MongoDB: {config.MONGO_DATABASE}")
    except ConnectionFailure as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        exit(1)
    finally:
        mongo_client.close()

ping_mongodb()

kafka_config = {
    'bootstrap.servers': config.KAFKA_BOOTSTRAP_SERVERS,
    'group.id': 'topic-lister',
    'auto.offset.reset': 'latest'
}

consumer = Consumer(kafka_config)
metadata = consumer.list_topics(timeout=10)
topics = metadata.topics.keys()

logger.info("📦 Available Kafka topics:")
for topic in topics:
    logger.info(f" - {topic}")

consumer.close()

admin_config = {
    'bootstrap.servers': config.KAFKA_BOOTSTRAP_SERVERS
}
admin_client = AdminClient(admin_config)
cluster_metadata = admin_client.list_topics(timeout=10)
existing_topics = set(cluster_metadata.topics.keys())

if isinstance(config.KAFKA_TOPICS, dict):
    topic_names = list(config.KAFKA_TOPICS.keys())
else:
    topic_names = list(config.KAFKA_TOPICS)

topics_to_create = []
for topic in topic_names:
    if topic not in existing_topics:
        logger.warning(f"Topic '{topic}' does not exist. Scheduling for creation.")
        topics_to_create.append(NewTopic(topic, num_partitions=1, replication_factor=1))
    else:
        logger.info(f"Topic '{topic}' already exists.")

if topics_to_create:
    fs = admin_client.create_topics(topics_to_create, validate_only=False)
    for topic, future in fs.items():
        try:
            future.result()
            logger.success(f"✅ Topic '{topic}' created successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to create topic '{topic}': {e}")
else:
    logger.info("✅ All required Kafka topics already exist.")"""
