from django.apps import AppConfig


class PriemkaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'priemka'

    def ready(self):
        import priemka.signals
