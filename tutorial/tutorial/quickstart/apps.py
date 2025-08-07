from django.apps import AppConfig

class QuickstartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quickstart'

    def ready(self):
        import quickstart.signals