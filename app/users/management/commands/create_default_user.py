from django.core.management.base import BaseCommand
from users.models import Users
import os


class Command(BaseCommand):
    help = "Create a superuser if none exists"

    def handle(self, *args, **options):
        existing_default_user = Users.objects.filter(
            email=os.getenv("DEFAULT_EMAIL")
        ).exists()

        if not existing_default_user:
            Users.objects.create(
                first_name="John",
                last_name="Doe",
                email=os.getenv("DEFAULT_EMAIL"),
                password=os.getenv("DEFAULT_PASSWORD"),
                role="student",
                is_active=True,
            )
            self.stdout.write(self.style.SUCCESS("Default user created."))
        else:
            self.stdout.write(self.style.SUCCESS("Default user already exists."))
