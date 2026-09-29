from django.core.management.base import BaseCommand
from confluent_kafka import Consumer
import json
from notification.models import Notification
from django.conf import settings 
from  django.db import IntegrityError 
class Command(BaseCommand):

    def handle(self, *args, **options):
        consumer = Consumer({
            "bootstrap.servers":settings.KAFKA_BOOTSTRAP_SERVERS,
            "group.id":"notification-service",
            "auto.offset.reset":"earliest",
            "enable.auto.commit":False
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
            try:    
                if event["event_type"] == "TICKET_CREATED":
                    Notification.objects.create(
                            user_id= event["customer_id"],
                            message = "Your Ticket Created",
                            event_type = event["event_type"],
                            event_id = event["event_id"]
                        )
                    print("Notification Saved!")

                elif event["event_type"] == "TICKET_ASSIGNED":
                                Notification.objects.create(
                                        user_id= event["customer_id"],
                                        message = "A ticket was assigned to you",
                                        event_type = event["event_type"],
                                        event_id = event["event_id"]
                                    )
                                print("Notification Saved!")   

                elif event["event_type"] == "TICKET_STATUS_CHANGED":
                                            Notification.objects.create(
                                                    user_id= event["customer_id"],
                                                    message = "A ticket was assigned to you",
                                                    event_type = event["event_type"],
                                                    event_id = event["event_id"]
                                                )
                                            print("Notification Saved!") 
                else: 
                        continue
                                            
            except IntegrityError:
                    print('Duplicate event ')

            consumer.commit(message=message)                                               