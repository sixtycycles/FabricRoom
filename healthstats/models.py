from django.db import models
from datetime import datetime
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.text import slugify


class Symptom(models.Model):
    name = models.SlugField(verbose_name='Symptom name',max_length=200, unique=True)    
    description = models.CharField(max_length=500, blank = True, null = True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('symptom_detail', args=[str(self.name)])
    #override save to save slug only on creation so urls dont change .
    

class HealthEvent(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    when = models.DateTimeField(auto_now_add=True)
    symptoms = models.ManyToManyField(Symptom, related_name='symptoms', blank=True)
    temperature = models.FloatField(verbose_name='temperatures',blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    feels_rating = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.author.first_name} - @{self.when}"

    def get_absolute_url(self):
        return reverse('stat_detail', args=[str(self.id)])




