from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

from utils.config import config
from utils.logger import setup_logger
from utils.fs_utils import ensure_path_exists
from datetime import datetime

class KafkaAvroProducer:
    """
    Universal Kafka Avro producer to serialize and publish messages to a Kafka topic.
    """
    def __init__(self, topic: str, schema_file: str):
        self.topic = topic
        current_date = datetime.now().strftime('%Y-%m-%d')
        log_path = f"logs/producer/producer_{current_date}.log"
        ensure_path_exists(log_path)
        self.logger = setup_logger("BlockProducer", log_path)
        self.logger.debug(f"🟡 Initializing KafkaAvroProducer for topic: {self.topic}")

        schema_path = config.SCHEMA_DIR / schema_file
        self.logger.debug(f"📄 Loading Avro schema from: {schema_path}")

        try:
            schema_str = schema_path.read_text()
            self.logger.info("✅ Avro schema loaded successfully.")
        except Exception:
            self.logger.exception("❌ Failed to read Avro schema file.")
            raise

        self.logger.debug("🔧 Configuring Schema Registry client.")
        schema_registry_client = SchemaRegistryClient({"url": config.SCHEMA_REGISTRY_URL})
        self.logger.info(f"✅ Connected to Schema Registry: {config.SCHEMA_REGISTRY_URL}")

        self.logger.debug("🧪 Creating Avro serializer.")
        avro_serializer = AvroSerializer(
            schema_registry_client=schema_registry_client,
            schema_str=schema_str,
            to_dict=lambda obj, ctx: obj,
        )

        self.logger.debug("⚙️ Initializing Kafka SerializingProducer.")
        self.producer = SerializingProducer({
            "bootstrap.servers": config.KAFKA_BOOTSTRAP_SERVERS,
            "key.serializer": StringSerializer("utf_8"),
            "value.serializer": avro_serializer,
            "message.max.bytes": 20000000
        })

        self.logger.info(f"✅ KafkaAvroProducer fully initialized for topic: {self.topic}")

    def produce(self, value: dict, key: str = None):
        partition_key = key or str(value.get("user_id", "unknown"))
        self.logger.debug(f"📤 Preparing to produce message to topic: {self.topic} with key: {partition_key}")

        try:
            self.producer.produce(
                topic=self.topic,
                key=partition_key,
                value=value,
                on_delivery=self.delivery_report,
            )
            self.logger.info(f"🟢 Produce request enqueued to topic '{self.topic}' for key '{partition_key}'")
        except Exception:
            self.logger.exception("❌ KafkaAvroProducer: Produce failed")

    def flush(self):
        self.logger.debug("🌀 Flushing Kafka producer messages.")
        self.producer.flush()
        self.logger.info("✅ Kafka producer flushed successfully.")

    def delivery_report(self, err, msg):
        if err is not None:
            self.logger.error(f"❌ Delivery failed for key={msg.key()}: {err}")
        else:
            self.logger.info(
                f"📦 Delivered to topic={msg.topic()} | partition={msg.partition()} | offset={msg.offset()} | key={msg.key()}"
            )
