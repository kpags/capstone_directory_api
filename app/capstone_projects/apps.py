from django.apps import AppConfig


class CapstoneProjectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'capstone_projects'
    
    def ready(self) -> None:
        import capstone_projects.signals
