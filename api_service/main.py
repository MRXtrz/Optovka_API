from fastapi import FastAPI
from src.routers import auth, categories, subcategories, supplier, products
import os

app = FastAPI(title="Optoviki API", version="1.0")

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(subcategories.router)
app.include_router(supplier.router)
app.include_router(products.router)

if os.getenv("KAFKA_BOOTSTRAP_SERVERS"):
    from mykafka.consumer import KafkaConsumerService
    import threading
    consumer_service = KafkaConsumerService()
    threading.Thread(target=consumer_service.run, daemon=True).start()
