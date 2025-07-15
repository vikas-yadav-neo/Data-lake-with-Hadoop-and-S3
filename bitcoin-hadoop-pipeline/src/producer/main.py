import asyncio
from producer.block_producer import BlockProducer

async def run():
    """
    Main coroutine to produce Bitcoin block data to Kafka using block height range.
    """
    producer = BlockProducer(topic="raw-blocks", schema_file="block_schema.avsc")
    producer.logger.info("🚀 Starting BlockProducer pipeline...")
    await producer.produce_by_height_range(840000, 840005)
    producer.logger.info("✅ BlockProducer run completed.")

if __name__ == "__main__":
    asyncio.run(run())
