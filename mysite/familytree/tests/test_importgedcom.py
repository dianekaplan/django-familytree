from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

from django.core.management.base import CommandError
from django.test import TestCase

from familytree.management.commands.importgedcom import Command
from familytree.models import Family, Person


class ImportGedcomCommandTests(TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.command = Command()
        self.command.stdout = StringIO()

    def test_add_arguments(self):
        """Test that the command accepts file name argument."""
        parser = Mock()
        self.command.add_arguments(parser)
        parser.add_argument.assert_called_once()
        call_args = parser.add_argument.call_args
        assert call_args[0][0] == "file name"
        assert call_args[1]["type"] == Path

    def test_handle_raises_error_for_non_ged_file(self):
        """Test that command raises error when file extension is not .ged."""
        with self.assertRaises(CommandError) as context:
            self.command.handle(**{"file name": Path("test.txt")})
        assert "Please specify GEDCOM file" in str(context.exception)

    def test_handle_raises_error_for_nonexistent_file(self):
        """Test that command raises error when file does not exist."""
        with self.assertRaises(CommandError) as context:
            self.command.handle(**{"file name": Path("nonexistent.ged")})
        assert "does not exist" in str(context.exception)

    def test_validate_person_ids_unique_success(self):
        """Test validation passes when all person IDs are unique."""
        mock_record1 = Mock()
        mock_record2 = Mock()

        with patch.object(self.command, "check_record_for_unique_id") as mock_check:
            mock_check.side_effect = ["UUID1", "UUID2"]
            person_records = [mock_record1, mock_record2]

            result, message = self.command.validate_person_ids_unique(person_records)

            assert result is True
            assert message is None

    def test_validate_person_ids_unique_fails_on_duplicate(self):
        """Test validation fails when duplicate person IDs are found."""
        mock_record1 = Mock()
        mock_record2 = Mock()

        with patch.object(self.command, "check_record_for_unique_id") as mock_check:
            mock_check.side_effect = ["UUID1", "UUID1"]
            person_records = [mock_record1, mock_record2]

            result, message = self.command.validate_person_ids_unique(person_records)

            assert result is False
            assert "UUID1" in message
            assert "not unique" in message

    def test_check_record_for_unique_id_with_aka_fact(self):
        """Test extracting unique ID from FACT/AKA/NOTE structure."""
        mock_note = Mock()
        mock_note.__str__ = Mock(return_value="2 NOTE test-uuid-123\r\n")

        mock_type = Mock()
        mock_type.__str__ = Mock(return_value="2 TYPE AKA")

        mock_fact = Mock()
        mock_fact.__str__ = Mock(return_value="1 FACT")
        mock_fact.get_child_elements.return_value = [mock_type, mock_note]

        mock_record = Mock()
        mock_record.get_child_elements.return_value = [mock_fact]

        result = self.command.check_record_for_unique_id(mock_record)

        assert result == "test-uuid-123"

    def test_check_record_for_unique_id_without_aka_fact(self):
        """Test that None is returned when no AKA FACT is present."""
        mock_fact = Mock()
        mock_fact.__str__ = Mock(return_value="1 FACT")
        mock_fact.get_child_elements.return_value = []

        mock_record = Mock()
        mock_record.get_child_elements.return_value = [mock_fact]

        result = self.command.check_record_for_unique_id(mock_record)

        assert result is None

    def test_check_record_for_unique_id_no_fact_element(self):
        """Test that None is returned when no FACT element exists."""
        mock_record = Mock()
        mock_record.get_child_elements.return_value = []

        result = self.command.check_record_for_unique_id(mock_record)

        assert result is None

    def test_check_db_for_person_with_id_finds_person(self):
        """Test finding a person in database by gedcom_uuid."""
        person = Person.objects.create(
            display_name="Test Person", gedcom_uuid="unique-id-123", first="Test", last="Person"
        )

        result = self.command.check_db_for_person_with_id("unique-id-123", "Test Person")

        assert result == person

    def test_check_db_for_person_with_id_no_match(self):
        """Test that None is returned when no person matches the ID."""
        result = self.command.check_db_for_person_with_id("nonexistent-id", "Test Person")

        assert result is None

    def test_handle_person_creates_new_person(self):
        """Test that handle_person creates a new Person record."""
        mock_element = Mock()
        mock_element.get_name.return_value = ("John", "Doe")
        mock_element.get_birth_data.return_value = ("1 Jan 1980", "New York", [])
        mock_element.get_gender.return_value = "M"
        mock_element.get_occupation.return_value = "Engineer"
        mock_element.get_death_data.return_value = ("", "", [])
        mock_element.__str__ = Mock(return_value="0 @I1@ INDI\r\n")
        mock_element.get_child_elements.return_value = []

        initial_count = Person.objects.count()
        self.command.handle_person(mock_element)

        assert Person.objects.count() == initial_count + 1
        person = Person.objects.last()
        assert person.first == "John"
        assert person.last == "Doe"
        assert person.display_name == "John Doe"
        assert person.birthdate_note == "1 Jan 1980"
        assert person.birthplace == "New York"
        assert person.sex == "M"
        assert person.work == "Engineer"
        assert person.gedcom_indi == "@I1@"

    def test_handle_person_skips_person_in_skip_list(self):
        """Test that handle_person skips people in the skip list."""
        mock_element = Mock()
        mock_element.get_name.return_value = ("John", "Doe")
        mock_element.get_birth_data.return_value = ("", "", [])
        mock_element.get_gender.return_value = "M"
        mock_element.get_occupation.return_value = ""
        mock_element.get_death_data.return_value = ("", "", [])
        mock_element.__str__ = Mock(return_value="0 @I1@ INDI\r\n")

        self.command.person_skip_list = ["John Doe"]
        initial_count = Person.objects.count()

        self.command.handle_person(mock_element)

        assert Person.objects.count() == initial_count
        assert self.command.person_skipped_count == 1

    def test_handle_person_updates_existing_person(self):
        """Test that handle_person updates existing person with matching UUID."""
        existing_person = Person.objects.create(
            display_name="John Doe", gedcom_uuid="unique-id-123", first="John", last="Doe"
        )

        mock_note = Mock()
        mock_note.__str__ = Mock(return_value="2 NOTE unique-id-123\r\n")
        mock_type = Mock()
        mock_type.__str__ = Mock(return_value="2 TYPE AKA")
        mock_fact = Mock()
        mock_fact.__str__ = Mock(return_value="1 FACT")
        mock_fact.get_child_elements.return_value = [mock_type, mock_note]

        mock_element = Mock()
        mock_element.get_name.return_value = ("John", "Doe")
        mock_element.get_birth_data.return_value = ("", "", [])
        mock_element.get_gender.return_value = "M"
        mock_element.get_occupation.return_value = ""
        mock_element.get_death_data.return_value = ("", "", [])
        mock_element.__str__ = Mock(return_value="0 @I2@ INDI\r\n")
        mock_element.get_child_elements.return_value = [mock_fact]

        initial_count = Person.objects.count()
        self.command.handle_person(mock_element)

        # Should not create new person
        assert Person.objects.count() == initial_count

        # Should update gedcom_indi
        existing_person.refresh_from_db()
        assert existing_person.gedcom_indi == "@I2@"
        assert self.command.person_skipped_count == 1

    def test_handle_family_creates_family_with_both_parents(self):
        """Test that handle_family creates a Family record when both parents exist."""
        wife = Person.objects.create(display_name="Jane Doe", gedcom_indi="@I1@", first="Jane", last="Doe")
        husband = Person.objects.create(display_name="John Doe", gedcom_indi="@I2@", first="John", last="Doe")

        mock_wife_element = Mock()
        mock_wife_element.__str__ = Mock(return_value="1 WIFE @I1@\r\n")

        mock_husband_element = Mock()
        mock_husband_element.__str__ = Mock(return_value="1 HUSB @I2@\r\n")

        mock_element = Mock()
        mock_element.__str__ = Mock(return_value="0 @F1@ FAM\r\n")
        mock_element.get_child_elements.return_value = [mock_wife_element, mock_husband_element]

        initial_count = Family.objects.count()
        self.command.handle_family(mock_element)

        assert Family.objects.count() == initial_count + 1
        family = Family.objects.last()
        assert family.wife == wife
        assert family.husband == husband
        assert family.display_name == "Jane Doe & John Doe"
        assert family.gedcom_indi == "@F1@"

    def test_handle_family_does_not_create_with_only_one_parent(self):
        """Test that handle_family does not create Family when only one parent exists."""
        wife = Person.objects.create(display_name="Jane Doe", gedcom_indi="@I1@", first="Jane", last="Doe")

        mock_wife_element = Mock()
        mock_wife_element.__str__ = Mock(return_value="1 WIFE @I1@\r\n")

        mock_element = Mock()
        mock_element.__str__ = Mock(return_value="0 @F1@ FAM\r\n")
        mock_element.get_child_elements.return_value = [mock_wife_element]

        initial_count = Family.objects.count()
        self.command.handle_family(mock_element)

        # Should not create family with only one parent
        assert Family.objects.count() == initial_count

        # Verify the wife person still exists but is not part of any family
        wife.refresh_from_db()
        assert wife.display_name == "Jane Doe"
        assert not Family.objects.filter(wife=wife).exists()

    def test_handle_family_tracks_children(self):
        """Test that handle_family tracks child-family associations."""
        wife = Person.objects.create(display_name="Jane Doe", gedcom_indi="@I1@", first="Jane", last="Doe")
        husband = Person.objects.create(display_name="John Doe", gedcom_indi="@I2@", first="John", last="Doe")
        child = Person.objects.create(display_name="Baby Doe", gedcom_indi="@I3@", first="Baby", last="Doe")

        mock_wife_element = Mock()
        mock_wife_element.__str__ = Mock(return_value="1 WIFE @I1@\r\n")

        mock_husband_element = Mock()
        mock_husband_element.__str__ = Mock(return_value="1 HUSB @I2@\r\n")

        mock_child_element = Mock()
        mock_child_element.__str__ = Mock(return_value="1 CHIL @I3@\r\n")

        mock_element = Mock()
        mock_element.__str__ = Mock(return_value="0 @F1@ FAM\r\n")
        mock_element.get_child_elements.return_value = [mock_wife_element, mock_husband_element, mock_child_element]

        self.command.handle_family(mock_element)

        # Verify family was created with correct parents
        family = Family.objects.get(gedcom_indi="@F1@")
        assert family.wife == wife
        assert family.husband == husband

        # Verify child is tracked in child_family_dict
        assert child.gedcom_indi in self.command.child_family_dict
        assert self.command.child_family_dict[child.gedcom_indi] == family.gedcom_indi

    def test_handle_family_updates_existing_family(self):
        """Test that handle_family updates existing Family record."""
        wife = Person.objects.create(display_name="Jane Doe", gedcom_indi="@I1@", first="Jane", last="Doe")
        husband = Person.objects.create(display_name="John Doe", gedcom_indi="@I2@", first="John", last="Doe")

        # Create existing family
        existing_family = Family.objects.create(display_name="Jane Doe & John Doe", wife=wife, husband=husband)

        mock_wife_element = Mock()
        mock_wife_element.__str__ = Mock(return_value="1 WIFE @I1@\r\n")

        mock_husband_element = Mock()
        mock_husband_element.__str__ = Mock(return_value="1 HUSB @I2@\r\n")

        mock_element = Mock()
        mock_element.__str__ = Mock(return_value="0 @F1@ FAM\r\n")
        mock_element.get_child_elements.return_value = [mock_wife_element, mock_husband_element]

        initial_count = Family.objects.count()
        self.command.handle_family(mock_element)

        # Should not create new family
        assert Family.objects.count() == initial_count

        # Should update gedcom_indi
        existing_family.refresh_from_db()
        assert existing_family.gedcom_indi == "@F1@"

    def test_add_person_family_values(self):
        """Test that add_person_family_values links children to their origin families."""
        wife = Person.objects.create(display_name="Jane Doe", gedcom_indi="@I1@", first="Jane", last="Doe")
        husband = Person.objects.create(display_name="John Doe", gedcom_indi="@I2@", first="John", last="Doe")
        child = Person.objects.create(display_name="Baby Doe", gedcom_indi="@I3@", first="Baby", last="Doe")

        family = Family.objects.create(
            display_name="Jane Doe & John Doe", gedcom_indi="@F1@", wife=wife, husband=husband
        )

        self.command.child_family_dict = {"@I3@": "@F1@"}
        self.command.add_person_family_values()

        child.refresh_from_db()
        assert child.family == family

    def test_find_existing_family_record_finds_match(self):
        """Test that find_existing_family_record finds matching family."""
        wife = Person.objects.create(display_name="Jane Doe", first="Jane", last="Doe")
        husband = Person.objects.create(display_name="John Doe", first="John", last="Doe")

        family = Family.objects.create(display_name="Jane Doe & John Doe", wife=wife, husband=husband)

        result = self.command.find_existing_family_record(wife, husband)

        assert result == family

    def test_find_existing_family_record_no_match(self):
        """Test that find_existing_family_record returns None when no match."""
        wife = Person.objects.create(display_name="Jane Doe", first="Jane", last="Doe")
        husband = Person.objects.create(display_name="John Doe", first="John", last="Doe")

        result = self.command.find_existing_family_record(wife, husband)

        assert result is None

    def test_make_string_from_date_valid_date(self):
        """Test parsing a valid date string."""
        result = self.command.make_string_from_date("1 Jan 1980")

        assert result is not None
        assert result.year == 1980
        assert result.month == 1
        assert result.day == 1

    def test_make_string_from_date_too_short(self):
        """Test that short date string returns None."""
        result = self.command.make_string_from_date("1980")

        assert result is None

    def test_make_string_from_date_insufficient_parts(self):
        """Test that date string with insufficient parts returns None."""
        result = self.command.make_string_from_date("Jan 1980")

        assert result is None

    def test_make_string_from_date_invalid_format(self):
        """Test that invalid date string returns None."""
        result = self.command.make_string_from_date("not a date string")

        assert result is None

    def test_update_date_fields_with_valid_dates(self):
        """Test that update_date_fields populates date fields from note fields."""
        person = Person.objects.create(
            display_name="Test Person",
            first="Test",
            last="Person",
            birthdate_note="1 Jan 1980",
            deathdate_note="31 Dec 2050",
        )

        self.command.update_date_fields(person)

        person.refresh_from_db()
        assert person.birthdate is not None
        assert person.birthdate.year == 1980
        assert person.birthdate.month == 1
        assert person.birthdate.day == 1
        assert person.deathdate is not None
        assert person.deathdate.year == 2050

    def test_update_date_fields_with_invalid_dates(self):
        """Test that update_date_fields handles invalid date strings."""
        person = Person.objects.create(
            display_name="Test Person", first="Test", last="Person", birthdate_note="Abt 1980", deathdate_note="Unknown"
        )

        self.command.update_date_fields(person)

        person.refresh_from_db()
        # Should not set date fields when parsing fails
        assert person.birthdate is None
        assert person.deathdate is None

    def test_update_matching_person_record(self):
        """Test that update_matching_person_record updates gedcom_indi."""
        person = Person.objects.create(
            display_name="Test Person", gedcom_uuid="unique-id-123", first="Test", last="Person", gedcom_indi="@I1@"
        )

        mock_element = Mock()

        self.command.update_matching_person_record(person, mock_element, "@I2@")

        person.refresh_from_db()
        assert person.gedcom_indi == "@I2@"

    def test_counters_increment_correctly(self):
        """Test that command counters increment correctly."""
        assert self.command.gedcom_person_records == 0
        assert self.command.gedcom_family_records == 0
        assert self.command.person_added_count == 0
        assert self.command.family_added_count == 0
        assert self.command.person_skipped_count == 0

        # Create a simple person record
        mock_element = Mock()
        mock_element.get_name.return_value = ("John", "Doe")
        mock_element.get_birth_data.return_value = ("", "", [])
        mock_element.get_gender.return_value = "M"
        mock_element.get_occupation.return_value = ""
        mock_element.get_death_data.return_value = ("", "", [])
        mock_element.__str__ = Mock(return_value="0 @I1@ INDI\r\n")
        mock_element.get_child_elements.return_value = []

        self.command.handle_person(mock_element)

        assert self.command.gedcom_person_records == 1
        assert self.command.person_added_count == 1
