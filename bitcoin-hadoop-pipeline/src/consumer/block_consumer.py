from utils.kafka_consumer import KafkaAvroConsumer
from utils.hdfs_client import HadoopClient

class BlockConsumer:
    """
    Responsible for consuming Bitcoin block data from a Kafka topic using Avro deserialization.
    """

    def __init__(self, topic: str, schema_file: str, group_id: str):
        self.topic = topic
        self.kafka_consumer = KafkaAvroConsumer(
            topic=topic,
            schema_file=schema_file,
            group_id=group_id
        )
        self.logger = self.kafka_consumer.logger  # Inherit the logger
        self.hadoop_client = HadoopClient(
            hdfs_url="http://localhost:9870",
            user="neosoft"
        )
        self.logger.info(f"🧱 BlockConsumer initialized for topic: {self.topic}")

    def start(self):
        self.logger.info("🚀 Starting BlockConsumer loop.")
        hdfs_dir_path = "/user/neosoft/practice/data/bronze/blocks/"

        try:
            if not self.hadoop_client.exists(hdfs_dir_path):
                self.hadoop_client.mkdir(hdfs_dir_path)
                self.logger.info(f"📁 Created HDFS directory: {hdfs_dir_path}")
            else:
                self.logger.debug(f"📁 HDFS directory already exists: {hdfs_dir_path}")

            for data in self.kafka_consumer.consume_loop():
                block_height = data.get("height", "unknown")
                self.logger.debug(f"<UNK> Block height: {block_height}")
                hdfs_file_path = f"{hdfs_dir_path}block_{block_height}.json"
                self.logger.debug(f"📦 Writing block to HDFS: {hdfs_file_path}")
                self.hadoop_client.write(hdfs_file_path, data)
                self.logger.info(f"✅ Written block height {block_height} to HDFS.")

        except KeyboardInterrupt:
            self.logger.info("🛑 BlockConsumer interrupted by user.")
        except Exception as e:
            self.logger.error(f"❌ Error in BlockConsumer: {e}", exc_info=True)
        finally:
            self.kafka_consumer.close()
            self.logger.info("✅ BlockConsumer shut down cleanly.")
