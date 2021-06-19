from django.contrib.admin.options import ModelAdmin
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model


class Snack(models.Model):
    quantity = models.IntegerField()
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name

