import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

# Ensure paths are set correctly if needed, but in a command they already are
from stsv_app.seeders.clear_db import clear_database
from stsv_app.seeders.core_seeder import seed_core
from stsv_app.seeders.users_seeder import seed_users
from stsv_app.seeders.academics_seeder import seed_academics
from stsv_app.seeders.events_seeder import seed_events
from stsv_app.seeders.training_points_seeder import seed_training_points
from stsv_app.seeders.support_seeder import seed_support
from stsv_app.seeders.finance_seeder import seed_finance
from stsv_app.seeders.system_seeder import seed_system

class Command(BaseCommand):
    help = 'Seed database with comprehensive mock data covering all choices and dynamic time'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear the database before seeding')
        parser.add_argument('--students', type=int, default=50, help='Number of students to generate (default: 50)')
        parser.add_argument('--events', type=int, default=20, help='Number of events to generate (default: 20)')

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Seeding is only allowed in DEBUG mode (Development/Staging). Cannot run on Production.")

        should_clear = options['clear']
        num_students = options['students']
        num_events = options['events']

        if should_clear:
            self.stdout.write(self.style.WARNING("Clearing database..."))
            clear_database()
            self.stdout.write(self.style.SUCCESS("Database cleared successfully."))

        self.stdout.write("Starting to seed database...")

        try:
            with transaction.atomic():
                seed_core()
                seed_users(num_students=num_students)
                seed_academics(num_students=num_students)
                seed_training_points()
                seed_events(num_events=num_events)
                seed_finance()
                seed_support()
                seed_system()
            
            self.stdout.write(self.style.SUCCESS("Successfully seeded the database!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to seed database: {e}"))
            raise e
