from django.core.management.base import BaseCommand
from listings.models import Listing
from django.contrib.auth import get_user_model
from faker import Faker
import random

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Seed the database with sample listings'

    def handle(self, *args, **kwargs):
        host = User.objects.first()
        if not host:
            self.stdout.write(self.style.ERROR("No users found. Please create a user first."))
            return

        for _ in range(10):
            Listing.objects.create(
                host=host,
                name=fake.company(),
                description=fake.text(),
                location=fake.city(),
                price_per_night=round(random.uniform(50, 500), 2)
            )
        self.stdout.write(self.style.SUCCESS("Successfully seeded the database with sample listings"))
