import os
from django.core.management.base import BaseCommand
from core.models import User


class Command(BaseCommand):
    help = 'Create an admin superuser from environment variables if one does not exist'

    def handle(self, *args, **kwargs):
        username = os.environ.get('DJANGO_ADMIN_USER', 'admin')
        email = os.environ.get('DJANGO_ADMIN_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_ADMIN_PASSWORD', 'Admin1234!')

        if User.objects.filter(username=username).exists():
            self.stdout.write(f'Admin user "{username}" already exists — skipping.')
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role='company',
        )
        self.stdout.write(self.style.SUCCESS(f'Admin user "{username}" created successfully.'))
