from typing import Any
from confluent_kafka import Consumer, KafkaError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

from utils.config import config
from utils.logger import setup_logger
from datetime import datetime
from utils.fs_utils import ensure_path_exists

class KafkaAvroConsumer:
    """
    Universal Kafka Avro consumer that consumes and deserializes messages from a specified Kafka topic.
    Uses Confluent Schema Registry for Avro schema deserialization.
    """

    def __init__(self, topic: str, schema_file: str, group_id: str):
        self.topic = topic
        self.group_id = group_id

        schema_path = config.SCHEMA_DIR / schema_file
        schema_str = schema_path.read_text()

        self.deserializer = AvroDeserializer(
            schema_registry_client=SchemaRegistryClient({"url": config.SCHEMA_REGISTRY_URL}),
            schema_str=schema_str,
            from_dict=lambda d, ctx: d,
        )

        self.consumer = Consumer({
            "bootstrap.servers": config.KAFKA_BOOTSTRAP_SERVERS,
            "group.id": self.group_id,
            "auto.offset.reset": "latest",
            "enable.auto.commit": True,
        })

        self.consumer.subscribe([self.topic])

        current_date = datetime.now().strftime('%Y-%m-%d')
        log_path = f"logs/producer/producer_{current_date}.log"
        ensure_path_exists(log_path)
        self.logger = setup_logger("BlockConsumer", log_path)
        self.logger.info(f"✅ Subscribed to Kafka topic: {self.topic}")

    def consume_loop(self):
        """
        Infinite generator that yields deserialized messages from Kafka.
        """
        self.logger.info("🚀 Kafka consumer loop started.")
        while True:
            msg = self.consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    self.logger.error(f"❌ Kafka error: {msg.error()}")
                continue

            try:
                context = SerializationContext(self.topic, MessageField.VALUE)
                value = self.deserializer(msg.value(), context)
                if value:
                    yield value
            except Exception as e:
                self.logger.exception("❌ Avro deserialization failed.", exc_info=e)

    def close(self):
        """
        Gracefully close the Kafka consumer.
        """
        self.consumer.close()
        self.logger.info("🔒 Kafka consumer connection closed.")
