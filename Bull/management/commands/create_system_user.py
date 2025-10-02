from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import secrets

class Command(BaseCommand):
    help = 'Create or update a system admin user (username: system) used for automated records'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'system'
        password = secrets.token_urlsafe(10)
        user = User.objects.filter(username=username).first()
        if user:
            self.stdout.write(self.style.WARNING(f"User '{username}' already exists. Updating role to admin and setting password."))
            user.role = 'admin'
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
        else:
            user = User.objects.create_user(username=username, password=password, email='system@localhost')
            user.role = 'admin'
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created system user '{username}'."))
        self.stdout.write(self.style.SUCCESS(f"Username: {username}"))
        self.stdout.write(self.style.SUCCESS(f"Password: {password}"))
        self.stdout.write(self.style.WARNING("Please change this password after first use and restrict access."))
