from django.apps import AppConfig


class MainConfig(AppConfig):
    name = "main"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):  # method just to import the signals
        import main.signals
