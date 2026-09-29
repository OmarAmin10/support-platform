from django.db import models

# Create your models here.

class Ticket(models.Model):
    STATUS_CHOICES = [
        ("OPEN","Open"),
        ("IN_PROGRESS","In progress"),
        ("RESOLVED","Resolved"),
        ("CLOSED","Delivered"),
    ]

    PRIORITY_CHOICES = [
            ("LOW","Low"),
            ("HIGH","High"),
            ("MEDIUM","Medium"),
            ("URGENT","Urgent"),
        ] 
    title = models.CharField(max_length=20)
    description = models.CharField(max_length=20)
    customer_id = models.IntegerField(max_length=1)
    assigned_agent_id = models.IntegerField(max_length=1,null=True)
    status = models.CharField(
        choices=STATUS_CHOICES,
        default="OPEN",
        max_length=20
    )
    priority = models.CharField(
        choices=PRIORITY_CHOICES,
        default="LOW",
        max_length=20
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
