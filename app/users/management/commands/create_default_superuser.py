from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = 'Create a superuser if none exists'
    
    def handle(self, *args, **options):
        existing_admin = User.objects.filter(email=os.getenv("SUPERUSER_EMAIL"), username=os.getenv("SUPERUSER_USERNAME")).exists()
        
        if not existing_admin:
            User.objects.create_superuser(
                username=os.getenv("SUPERUSER_USERNAME"),
                email=os.getenv("SUPERUSER_EMAIL"),
                password=os.getenv("SUPERUSER_PASSWORD")
            )
            self.stdout.write(self.style.SUCCESS('Superuser created.'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser already exists.'))
