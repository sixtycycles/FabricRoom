from django.db import models
from django.contrib.auth import get_user_model

class EventType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class HealthEvent(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE)
    when = models.DateTimeField(auto_now_add=True)
    value = models.FloatField(default=0.00,)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.author.first_name} - {self.event_type}@{self.when}"

