from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

from utils.logger import logger
from utils.config import config


class KafkaAvroDeserializer:
    def __init__(self, schema_file: str):
        """
        schema_file: schema filename inside config.SCHEMA_DIR, e.g., "user_events.avsc"
        """
        try:
            self.schema_path = config.SCHEMA_DIR / schema_file
            logger.info("📄 Loading schema from %s", self.schema_path)

            self.schema_str = self.schema_path.read_text()

            self.schema_registry = SchemaRegistryClient({
                "url": config.SCHEMA_REGISTRY_URL
            })

            self.deserializer = AvroDeserializer(
                schema_registry_client=self.schema_registry,
                schema_str=self.schema_str,
                from_dict=lambda d, ctx: d  # Optional: inject a domain model
            )

            logger.info("✅ AvroDeserializer initialized for schema: %s", schema_file)
        except Exception as e:
            logger.exception("❌ Failed to initialize KafkaAvroDeserializer")
            raise

    def deserialize(self, raw_value: bytes, topic: str):
        """
        Deserialize the message with proper SerializationContext.
        """
        try:
            context = SerializationContext(topic, MessageField.VALUE)
            return self.deserializer(raw_value, context)
        except Exception as e:
            logger.exception("❌ Failed to deserialize Kafka message")
            raise
