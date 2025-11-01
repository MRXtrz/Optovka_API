from kafka import KafkaProducer
import json
from datetime import datetime

class KafkaNotifier:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def notify_update(self, category_slug: str):
        self.producer.send('data_updated', {'category': category_slug, 'updated_at': str(datetime.now())})
        self.producer.flush()