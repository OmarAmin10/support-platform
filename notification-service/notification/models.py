from django.db import models

class Notification(models.Model):
    event_id = models.UUIDField(unique=True,null=True)
    user_id = models.IntegerField()
    message = models.TextField()
    event_type = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)
