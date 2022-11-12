from django.apps import AppConfig


class HealthstatsConfig(AppConfig):
    name = "healthstats"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):  # method just to import the signals
        import healthstats.signals
