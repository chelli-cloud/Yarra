from django.apps import AppConfig


class CompetitionsConfig(AppConfig):
    name = 'competitions'

    def ready(self):
        # Import signals to register them
        import competitions.signals
