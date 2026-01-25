from datetime import date

from django.core.management import call_command
from django.test import TestCase

from familytree.models import Person


class PopulateBirthYearCommandTests(TestCase):
    def run_command(self):
        call_command("populateBirthYear")

    def test_sets_birthyear_from_birthdate(self):
        person = Person.objects.create(
            display_name="From Birthdate",
            birthdate=date(1990, 5, 17),
            birthyear=None,
        )
        self.run_command()
        person.refresh_from_db()
        assert person.birthyear == 1990

    def test_sets_birthyear_from_birthdate_note_single_match(self):
        person = Person.objects.create(
            display_name="From Birthdate Note",
            birthdate_note="Abt. 1985",
            birthyear=None,
        )
        self.run_command()
        person.refresh_from_db()
        assert person.birthyear == 1985

    def test_does_not_set_when_multiple_matches_in_note(self):
        person = Person.objects.create(
            display_name="Multiple Matches",
            birthdate_note="between 1980 and 1981",
            birthyear=None,
        )
        self.run_command()
        person.refresh_from_db()
        assert person.birthyear is None

    def test_does_not_set_when_no_birth_info(self):
        person = Person.objects.create(
            display_name="No Birth Info",
            birthyear=None,
        )
        self.run_command()
        person.refresh_from_db()
        assert person.birthyear is None

    def test_does_not_modify_existing_birthyear(self):
        person = Person.objects.create(
            display_name="Existing Birthyear",
            birthyear=1975,
            birthdate=date(1976, 1, 1),
            birthdate_note="1977",
        )
        self.run_command()
        person.refresh_from_db()
        assert person.birthyear == 1975
