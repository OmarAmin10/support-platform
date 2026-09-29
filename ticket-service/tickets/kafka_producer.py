from confluent_kafka import Producer
import json
import os 
from dotenv import load_dotenv
import uuid

producer = Producer({
    "bootstrap.servers":os.getenv("KAFKA_BOOTSTRAP_SERVERS")
})


def publish_event(topic,event):
    event["event_id"]=str(uuid.uuid4())
    producer.produce(
        topic,
        value=json.dumps(event)
    )

    producer.flush()