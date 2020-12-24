from django.contrib import admin
from healthstats.models import HealthEvent, Symptom


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    pass

@admin.register(HealthEvent)
class HealthEventAdmin(admin.ModelAdmin):
    pass