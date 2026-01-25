from datetime import date
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from familytree.models import Person

FIXED_TODAY = date(2025, 1, 1)


class PopulateLivingBoolCommandTests(TestCase):
    def run_command(self):
        call_command("populateLivingBool")

    @patch("familytree.management.commands.populateLivingBool.date")
    def test_sets_living_true_when_young_birthyear(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        person = Person.objects.create(
            display_name="Young Birthyear",
            living=False,
            birthyear=2010,
            deathdate=None,
            deathdate_note=None,
        )
        self.run_command()
        person.refresh_from_db()
        assert person.living is True

    @patch("familytree.management.commands.populateLivingBool.date")
    def test_sets_living_true_when_recent_birthdate(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        person = Person.objects.create(
            display_name="Recent Birthdate",
            living=False,
            birthdate=date(2010, 6, 1),
            deathdate=None,
            deathdate_note=None,
        )
        self.run_command()
        person.refresh_from_db()
        assert person.living is True

    @patch("familytree.management.commands.populateLivingBool.date")
    def test_sets_living_true_when_birthdate_note_year_only(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        person = Person.objects.create(
            display_name="Birthdate Note Year",
            living=False,
            birthdate_note="2010",
            deathdate=None,
            deathdate_note=None,
        )
        self.run_command()
        person.refresh_from_db()
        assert person.living is True

    @patch("familytree.management.commands.populateLivingBool.date")
    def test_sets_living_true_when_birthdate_note_abt(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        person = Person.objects.create(
            display_name="Birthdate Note Abt",
            living=False,
            birthdate_note="Abt. 2010",
            deathdate=None,
            deathdate_note=None,
        )
        self.run_command()
        person.refresh_from_db()
        assert person.living is True

    @patch("familytree.management.commands.populateLivingBool.date")
    def test_sets_living_false_when_deathdate_present(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        person = Person.objects.create(
            display_name="Has Deathdate",
            living=True,
            deathdate=date(2020, 1, 1),
        )
        self.run_command()
        person.refresh_from_db()
        assert person.living is False

    @patch("familytree.management.commands.populateLivingBool.date")
    def test_sets_living_false_when_birthyear_older_than_100(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        person = Person.objects.create(
            display_name="Old Birthyear",
            living=True,
            birthyear=1925,  # 2025 - 1925 == 100
        )
        self.run_command()
        person.refresh_from_db()
        assert person.living is False

    @patch("familytree.management.commands.populateLivingBool.date")
    def test_sets_living_false_when_birthdate_note_old(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        person = Person.objects.create(
            display_name="Old Birthdate Note",
            living=True,
            birthdate_note="abt 1900",
        )
        self.run_command()
        person.refresh_from_db()
        assert person.living is False

    @patch("familytree.management.commands.populateLivingBool.date")
    def test_does_not_change_false_with_death_info(self, mock_date):
        mock_date.today.return_value = FIXED_TODAY
        person = Person.objects.create(
            display_name="False With Death Info",
            living=False,
            birthyear=2010,  # Would otherwise qualify to set True
            deathdate_note="Died",
        )
        self.run_command()
        person.refresh_from_db()
        assert person.living is False
