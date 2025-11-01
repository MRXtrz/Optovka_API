import os
from kafka import KafkaConsumer
import json
import logging
import time

logger = logging.getLogger(__name__)

class KafkaConsumerService:
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        self.topic = 'data_updated'
        self.consumer = None

    def _connect(self):
        attempts = 0
        while True:
            try:
                self.consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=[self.bootstrap_servers],
                    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                )
                logger.info("Connected to Kafka at %s", self.bootstrap_servers)
                return
            except Exception as e:
                attempts += 1
                wait = min(30, 1 + attempts)
                logger.warning("Kafka not available yet (%s). Retrying in %ss", e, wait)
                time.sleep(wait)

    def run(self):
        if not self.consumer:
            self._connect()
        for message in self.consumer:
            logger.info(f"Data updated: {message.value}")
