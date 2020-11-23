from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'main'

    def ready(self):  # method just to import the signals
        import main.signals
