from confluent_kafka import Consumer
import json
from .models import Notification
from  django.db import IntegrityError
consumer = Consumer({
    "bootstrap.servers":"localhost:9092",
    "group.id":"notification-service",
    "auto.offset.reset":"earliest",
})

consumer.subscribe(['ticket-events'])

while True:
    message = consumer.poll(1.0)

    if message is None:
        continue 
    if message.error():
         print("kafkaError:",message.error())
         continue

    value = message.value().decode("utf-8")
    event = json.loads(value)

    if Notification.objects.filter(event_id= event["event_id"]).exists():
        consumer.commit(message=message)
        continue
    if event["event_type"] == "TICKET_CREATED":
        Notification.objects.create(
            user_id= event["customer_id"],
            message = event["Your Ticket Created"],
            event_type = event["event_type"]
        )
        print("Notification Saved")