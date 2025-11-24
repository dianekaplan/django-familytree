import os
from contextlib import nullcontext

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from faker import Faker

from ...models import Branch, Family, Person

"""Context:
To anonymize data initializing the demo site, this script replaces surnames
"""


class Command(BaseCommand):
    help = "For demo site data anonymization: update surname values in person and family records (internal use)"

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

    suttell_variations = {"Suttell", "Suttle", "Suttel", "Suttelle", "Suttells", "Suttles", "Suttels", "Suttelles"}

    def determine_replacement_name(self, name) -> str:
        branch_lastnames = list(Branch.objects.values_list("display_name", flat=True).distinct())
        branch_mappings = {"Husband": "Adams", "Keem": "Barvian", "Kemler": "Cohen", "Kobrin": "Davies"}
        if name in branch_lastnames:
            return branch_mappings[name]
        else:
            fake = Faker()
            return fake.last_name()

    def update_person_record_lastname(self, person, name, replacement_name):
        new_lastname_value = None
        if person.last == name:
            new_lastname_value = replacement_name
        elif person.last and name in person.last:  # handle hyphenated cases, etc
            new_lastname_value = person.last.replace(name, replacement_name)
        if new_lastname_value:
            old = person.last
            person.last = new_lastname_value
            self.stdout.write(f"Update person last: {old} -> {new_lastname_value}")
            if not getattr(self, "dry_run", True):
                person.save()

    def update_person_record_displayname(self, person, name, replacement_name):
        name_groupings = person.display_name.split(" ", 1)
        portion_after_first_name = ""
        if len(name_groupings) > 1:
            portion_after_first_name = name_groupings[1]
            portion_contents = portion_after_first_name.split(" ")
        else:
            return  # if we have only a firstname, no update to make

        # For Suttells, we might replace a different value from the last name (avoid replacing Suttel within Suttell)
        if name in self.suttell_variations:
            thing_to_replace = self.get_variation_to_replace(name, replacement_name, portion_contents)
        elif name in portion_after_first_name:  # don't replace first names (if surname is also a first name)
            thing_to_replace = name
        else:
            return  # last name only appeared in display_name as first portion (skip)
        replacement_display_name = person.display_name.replace(thing_to_replace, replacement_name)
        self.stdout.write(f"Update person display_name: {person.display_name} -> {replacement_display_name}")
        person.display_name = replacement_display_name
        if not getattr(self, "dry_run", True):
            person.save()

    # To handle Suttell variations, find which variation is in the display_name
    def get_variation_to_replace(self, name, replacement_name, display_name_pieces):
        thing_to_replace = list(set(self.suttell_variations).intersection(display_name_pieces))
        return thing_to_replace[0]

    def update_family_record_displayname(self, family, name, replacement_name):
        pieces_of_display_name = family.display_name.split(" ")
        if name in self.suttell_variations:
            thing_to_replace = self.get_variation_to_replace(name, replacement_name, pieces_of_display_name)
        else:
            thing_to_replace = name
        if thing_to_replace:
            old_display_name = family.display_name
            new_display_name = old_display_name.replace(thing_to_replace, replacement_name)
            self.stdout.write(f"Update family display_name from {old_display_name} to {new_display_name}")
            family.display_name = new_display_name
            if not getattr(self, "dry_run", True):
                family.save()

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

        # Choose an atomic context when performing real writes; otherwise use a no-op context
        atomic_ctx = transaction.atomic() if not self.dry_run else nullcontext()

        with atomic_ctx:
            # To avoid confusion, for people with firstnames that are surnames, switch those out,
            # otherwise these will currently get swapped (with a surname) in family display_name values
            confusing_names = ["George", "David", "Frank", "Kaplan"]
            people_with_confusing_firstnames = Person.objects.filter(first__in=confusing_names)
            for person in people_with_confusing_firstnames:
                fake = Faker()
                old_firstname = person.first
                new_firstname = fake.first_name_male()
                person.first = new_firstname
                self.stdout.write(f"Update person first from {old_firstname} to {new_firstname}")
                if not self.dry_run:
                    person.save()

            existing_lastnames = Person.objects.values_list("last", flat=True).distinct()
            existing_lastnames_cleaned = [name for name in existing_lastnames if name and name.strip() not in ("", "?")]

            for name in existing_lastnames_cleaned:
                if name in self.suttell_variations:  # treat these variations as one
                    replacement_name = "Yorke"
                else:
                    replacement_name = self.determine_replacement_name(name)

                # Update person records where last matches
                people_with_this_name = Person.objects.filter(last=name)
                for person in people_with_this_name:
                    self.update_person_record_lastname(person, name, replacement_name)

                # Update person records where last didn't match, but display_name includes it
                people_with_display_name_including_it = Person.objects.filter(display_name__icontains=name)
                for person in people_with_display_name_including_it:
                    self.update_person_record_displayname(person, name, replacement_name)

                # Update family records where display_name includes name
                families_with_this_name = Family.objects.filter(display_name__icontains=name)
                for family in families_with_this_name:
                    self.update_family_record_displayname(family, name, replacement_name)
