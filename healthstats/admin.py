from django.contrib import admin
from healthstats.models import HealthEvent, EventType


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(HealthEvent)
class HealthEventAdmin(admin.ModelAdmin):
    pass