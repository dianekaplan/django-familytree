from django.core.management import call_command
from django.test import TestCase

from familytree.models import Family, Person


class PopulateDirectFamilyNumbersCommandTests(TestCase):
    def run_command(self, root_family_id):
        # Positional argument is required by the command ("root family")
        call_command("populateDirectFamilyNumbers", root_family_id)

    def test_sets_numbers_for_root_and_parents(self):
        # Create root family and spouses
        root_family = Family.objects.create(display_name="Root Family")
        wife = Person.objects.create(display_name="Wife")
        husband = Person.objects.create(display_name="Husband")
        root_family.wife = wife
        root_family.husband = husband
        root_family.save()

        # Create the origin families for wife and husband
        wife_origin_family = Family.objects.create(display_name="Wife Origin Family")
        husband_origin_family = Family.objects.create(display_name="Husband Origin Family")

        # Link people to their origin families
        wife.family = wife_origin_family
        wife.save()
        husband.family = husband_origin_family
        husband.save()

        # Run the command
        self.run_command(root_family.id)

        # Refresh from DB and assert numbering
        root_family.refresh_from_db()
        wife_origin_family.refresh_from_db()
        husband_origin_family.refresh_from_db()

        assert root_family.direct_family_number == 1
        assert wife_origin_family.direct_family_number == 2  # 2 * 1
        assert husband_origin_family.direct_family_number == 3  # 2 * 1 + 1

    def test_recurses_to_grandparents_and_uses_existing_values(self):
        # Create root family and spouses
        root_family = Family.objects.create(display_name="Root Family")
        wife = Person.objects.create(display_name="Wife")
        husband = Person.objects.create(display_name="Husband")
        root_family.wife = wife
        root_family.husband = husband
        root_family.save()

        # Create wife origin family and set an existing number to ensure it is not overwritten
        wife_origin_family = Family.objects.create(display_name="Wife Origin Family", direct_family_number=100)
        wife.family = wife_origin_family
        wife.save()

        # Create husband origin family (no existing number)
        husband_origin_family = Family.objects.create(display_name="Husband Origin Family")
        husband.family = husband_origin_family
        husband.save()

        # For wife's origin family, create her parents (spouses of the wife's origin family)
        w_mother = Person.objects.create(display_name="Wife's Mother")
        w_father = Person.objects.create(display_name="Wife's Father")
        wife_origin_family.wife = w_mother
        wife_origin_family.husband = w_father
        wife_origin_family.save()

        # Their origin families (grandparents of the root family's wife)
        w_mother_origin_family = Family.objects.create(display_name="Wife's Mother Origin Family")
        w_father_origin_family = Family.objects.create(display_name="Wife's Father Origin Family")
        w_mother.family = w_mother_origin_family
        w_mother.save()
        w_father.family = w_father_origin_family
        w_father.save()

        # For husband's origin family, create his parents (spouses of the husband's origin family)
        h_mother = Person.objects.create(display_name="Husband's Mother")
        h_father = Person.objects.create(display_name="Husband's Father")
        husband_origin_family.wife = h_mother
        husband_origin_family.husband = h_father
        husband_origin_family.save()

        # Their origin families (grandparents of the root family's husband)
        h_mother_origin_family = Family.objects.create(display_name="Husband's Mother Origin Family")
        h_father_origin_family = Family.objects.create(display_name="Husband's Father Origin Family")
        h_mother.family = h_mother_origin_family
        h_mother.save()
        h_father.family = h_father_origin_family
        h_father.save()

        # Run the command
        self.run_command(root_family.id)

        # Refresh from DB
        root_family.refresh_from_db()
        wife_origin_family.refresh_from_db()
        husband_origin_family.refresh_from_db()
        w_mother_origin_family.refresh_from_db()
        w_father_origin_family.refresh_from_db()
        h_mother_origin_family.refresh_from_db()
        h_father_origin_family.refresh_from_db()

        # Root family always starts at 1
        assert root_family.direct_family_number == 1

        # Wife origin family keeps its preexisting value
        assert wife_origin_family.direct_family_number == 100

        # Recursion uses the existing value (100) for wife side
        assert w_mother_origin_family.direct_family_number == 200  # 2 * 100
        assert w_father_origin_family.direct_family_number == 201  # 2 * 100 + 1

        # Husband origin family gets assigned from root's value 1 -> 2*1+1 == 3
        assert husband_origin_family.direct_family_number == 3
        # Recursion on husband side uses 3
        assert h_mother_origin_family.direct_family_number == 6  # 2 * 3
        assert h_father_origin_family.direct_family_number == 7  # 2 * 3 + 1
