from django.contrib import admin
from healthstats.models import AppleHealthUpload, HealthEvent, Symptom, HeartRate


@admin.register(HeartRate)
class HeartRateAdmin(admin.ModelAdmin):
    list_display = ("author", "creation_date", "start_date", "end_date", "value")
    list_filter = ("author", "creation_date")


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    pass


@admin.register(HealthEvent)
class HealthEventAdmin(admin.ModelAdmin):
    fields = (
        "author",
        "symptoms",
        "temperature",
        "note",
    )
    list_display = (
        "author",
        "when",
    )
    list_filter = ("author",)


@admin.register(AppleHealthUpload)
class AppleHealthUploadAdmin(admin.ModelAdmin):
    fields = ("author", "health_data_xml", "is_processed",)
    list_display = ("author", "health_data_xml", "is_processed")
