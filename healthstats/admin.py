from django.contrib import admin
from healthstats.models import HealthEvent, Symptom


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    pass

@admin.register(HealthEvent)
class HealthEventAdmin(admin.ModelAdmin):
    fields = ('author', 'symptoms', 'temperature', 'note', 'feels_rating' )
    list_display = ('author', 'when', 'feels_rating')
    list_filter = ('author', 'feels_rating')
    