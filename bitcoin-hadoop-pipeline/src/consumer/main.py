from consumer.block_consumer import BlockConsumer

def run():
    """
    Main function to start consuming Bitcoin block data from Kafka.
    """
    consumer = BlockConsumer(
        topic="raw-blocks",
        schema_file="block_schema.avsc",
        group_id="block-consumer-group"
    )
    consumer.logger.info("🚀 Launching BlockConsumer pipeline...")
    consumer.start()
    consumer.logger.info("🏁 BlockConsumer run finished.")

if __name__ == "__main__":
    run()
