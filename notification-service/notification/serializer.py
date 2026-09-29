from rest_framework import serializers
from.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model= Notification
        fields = [
            'id',
            'user_id',
            'message',
            'event_type',
            "created_at",
            'event_id'
        ]
        read_only_fields=[
             'id',
             'user_id',
             'message',
             'event_type',
             "created_at",
             'event_id'

        ]