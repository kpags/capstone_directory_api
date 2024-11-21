from django.core.management.base import BaseCommand
from users.models import Users
import os


class Command(BaseCommand):
    help = "Create a superuser if none exists"

    def handle(self, *args, **options):
        existing_default_admin = Users.objects.filter(
            email=os.getenv("ADMIN_EMAIL"), role="administrator"
        ).exists()

        if not existing_default_admin:
            Users.objects.create(
                first_name="Admin",
                last_name="Doe",
                email=os.getenv("ADMIN_EMAIL"),
                password=os.getenv("ADMIN_PASSWORD"),
                role="administrator",
                is_active=True,
            )
            self.stdout.write(self.style.SUCCESS("Default Admin created."))
        else:
            self.stdout.write(self.style.SUCCESS("Default Admin already exists."))
