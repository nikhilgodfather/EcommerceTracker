from django.apps import AppConfig


class TrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Tracker'
    
    def ready(self):
        from .views import start_background_task
        start_background_task()
