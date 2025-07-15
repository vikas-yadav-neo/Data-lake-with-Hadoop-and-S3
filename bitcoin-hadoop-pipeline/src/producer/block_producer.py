import time

from utils.kafka_producer import KafkaAvroProducer
from utils.rpc_client import RPCClient
from utils.helpers import unix_to_block_height_range

class BlockProducer:
    """
    Responsible for fetching Bitcoin block data via RPC and producing it to a Kafka topic using Avro format.
    """

    def __init__(self, topic: str, schema_file: str):
        self.topic = topic
        self.kafka_producer = KafkaAvroProducer(topic=topic, schema_file=schema_file)
        self.logger = self.kafka_producer.logger
        self.logger.info(f"🧱 BlockProducer initialized for topic: {self.topic}")

    async def produce_by_height_range(self, start_height: int, end_height: int):
        from_height = min(start_height, end_height)
        to_height = max(start_height, end_height)

        self.logger.info(f"📦 Starting block production from height {from_height} to {to_height}")
        start_time = time.time()

        try:
            async with RPCClient() as rpc:
                for height in range(from_height, to_height + 1):
                    self.logger.debug(f"📡 Fetching block hash for height {height}")
                    block_hash = await rpc.call("getblockhash", [height])

                    self.logger.debug(f"🔗 Block hash for height {height}: {block_hash}")
                    block_hex = await rpc.call("getblock", [block_hash, 0])
                    block = await rpc.call("getblock", [block_hash, 1])
                    timestamp = block.get("time")
                    block['tx'] = [block['tx'][0]]
                    # block_data = {
                    #     "block_hex": block_hex,
                    #     "height": height,
                    #     "timestamp": timestamp,
                    # }

                    try:
                        self.kafka_producer.produce(block)
                        self.logger.info(f"✅ Block {height} produced to Kafka topic '{self.topic}'")
                    except Exception:
                        self.logger.exception(f"❌ Failed to produce block {height}")

        except Exception as e:
            self.logger.exception(f"❌ Block production failed at height range {from_height}-{to_height}: {e}")
            raise

        self.kafka_producer.flush()
        self.logger.info(f"🌀 All blocks flushed to Kafka.")

        elapsed = time.time() - start_time
        self.logger.info(f"⏱️ Finished producing blocks {from_height}-{to_height} in {elapsed:.2f} seconds")

    async def produce_by_time_range(self, start_ts: int, end_ts: int):
        self.logger.info(f"🕒 Converting timestamps to heights: {start_ts} to {end_ts}")
        start_time = time.time()

        try:
            async with RPCClient() as rpc:
                start_height, end_height = await unix_to_block_height_range(rpc, start_ts, end_ts)
                self.logger.info(f"📏 Timestamp range converted to heights: {start_height} - {end_height}")
                await self.produce_by_height_range(start_height, end_height)
        except Exception as e:
            self.logger.exception(f"❌ Failed to produce blocks by time range: {e}")
            raise

        elapsed = time.time() - start_time
        self.logger.info(f"⏱️ Finished producing blocks from time range in {elapsed:.2f} seconds")
