import os
from contextlib import nullcontext

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from faker import Faker

from ...models import Person

"""Context:
To anonymize data initializing the demo site, this script replaces birthday month and day values
"""


class Command(BaseCommand):
    help = "For demo site data anonymization: update month and day values for birthday in person records (internal use)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            action="store_true",
            help="Do not perform any DB writes (default).",
        )
        parser.add_argument(
            "--no-dry-run",
            dest="dry_run",
            action="store_false",
            help="Perform DB writes (opposite of --dry-run).",
        )
        parser.set_defaults(dry_run=True)

    def handle(self, **options):
        # store dry_run flag for helper methods
        self.dry_run = options.get("dry_run", True)

        # Enforce safety: require explicit env var on real runs
        if not self.dry_run:
            allow = os.environ.get("DEMO_UPDATE_SURNAMES_ALLOW", "").lower() in ("1", "true", "yes")
            if not allow:
                raise CommandError(
                    "Refusing to run with --no-dry-run: "
                    "DEMO_UPDATE_SURNAMES_ALLOW not set to a truthy value in the environment."
                )

        people_with_birthday_values = Person.objects.filter(birthdate__isnull=False)

        # Choose an atomic context when performing real writes; otherwise use a no-op context
        atomic_ctx = transaction.atomic() if not self.dry_run else nullcontext()

        with atomic_ctx:
            for person in people_with_birthday_values:
                old_birthday = person.birthdate
                birth_year = person.birthdate.year

                # preserve year, change month and day
                fake = Faker()
                new_date = fake.date_object().replace(year=birth_year)

                self.stdout.write(f"Would update person birthday from {old_birthday} to {new_date}")
                if not self.dry_run:
                    self.stdout.write(f"Update person birthday from {old_birthday} to {new_date}")
                    person.birthdate = new_date
                    person.save()
