from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db.models.functions import Lower


class Command(BaseCommand):
    help = 'Check duplicate user emails (case-insensitive).'

    def handle(self, *args, **options):
        user_model = get_user_model()
        duplicates = (
            user_model.objects.exclude(email='')
            .annotate(email_lower=Lower('email'))
            .values('email_lower')
            .annotate(total=Count('id'))
            .filter(total__gt=1)
            .order_by('email_lower')
        )

        if not duplicates:
            self.stdout.write(self.style.SUCCESS('No duplicate emails found'))
            return

        self.stdout.write(self.style.WARNING('Duplicate emails found:'))
        for item in duplicates:
            self.stdout.write(f"- {item['email_lower']} ({item['total']} users)")
