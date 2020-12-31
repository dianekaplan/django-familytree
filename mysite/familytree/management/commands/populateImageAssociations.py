from django.core.management.base import BaseCommand, CommandError
from ...models import Person, Branch, Family, Image
from pathlib import Path
import csv

class Command(BaseCommand):
    help = 'Populates display names for migrated database (internal use)'

    def add_arguments(self, parser):
        parser.add_argument('images file', type=Path, help='Images file with all but associations')
        parser.add_argument('image associations', type=Path, help='Image associations file')

    def add_person_branches(self):
        people = Person.objects.all()

        for person in people:
            if person.keem_line:
                branch_to_associate = Branch.objects.get(id=1)
                person.branches.add(branch_to_associate)
                person.save()
                print("Added " + branch_to_associate.display_name + " for: " + person.display_name)

            if person.husband_line:
                branch_to_associate = Branch.objects.get(id=2)
                person.branches.add(branch_to_associate)
                person.save()
                print("Added " + branch_to_associate.display_name + " for: " + person.display_name)

            if person.kemler_line:
                branch_to_associate = Branch.objects.get(id=3)
                person.branches.add(branch_to_associate)
                person.save()
                print("Added " + branch_to_associate.display_name + " for: " + person.display_name)

            if person.kaplan_line:
                branch_to_associate = Branch.objects.get(id=4)
                person.branches.add(branch_to_associate)
                person.save()
                print("Added " + branch_to_associate.display_name + " for: " + person.display_name)

    def add_family_branches_and_spouses(self, file):
        with open(file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            next(reader) # skip the heading row
            for row in reader:
                    contents = (', '.join(row)).split(",")
                    family_id = int(contents[0])
                    branch_value = contents[3]
                    family_to_update = Family.objects.get(id=family_id)

                    # Add branch association
                    if branch_value:
                        branch_id = int(branch_value)

                        if 0 < branch_id < 5:
                            branch_to_associate = Branch.objects.get(id=branch_value)
                            family_to_update.branches.add(branch_to_associate)
                            family_to_update.save()
                            print("associated " + branch_to_associate.display_name + " with " + family_to_update.display_name)

                    # add spouse relationships
                    wife_id = int(contents[1])
                    husband_id = int(contents[2])
                    try:
                        wife = Person.objects.get(id=wife_id)
                    except:
                        print("SKIPPING FAMILY " + family_to_update.display_name + " person_id not found: " + str(wife_id))
                    try:
                        husband = Person.objects.get(id=husband_id)
                    except:
                        print("SKIPPING FAMILY " + family_to_update.display_name + " person_id not found: " + str(husband_id))
                    family_to_update.wife = wife
                    family_to_update.husband = husband
                    family_to_update.save()

    def handle(self, *args, **kwargs):
        family_file = kwargs['family file']

        # validate that the user gave file with extension ged
        if family_file.suffix!= '.csv':
            raise CommandError('Please specify family csv file, ex: families_spouses_branches.csv')

        # Add branch associations to people
        self.add_person_branches()

        # Check that the files are there
        path = Path("familytree/management/commands/export_files/")
        path_plus_family_file = path.joinpath(family_file)

        # Add branch associations to families (uses file)
        if (path_plus_family_file.is_file()):
            self.add_family_branches_and_spouses(path_plus_family_file)
        else:
            raise CommandError(family_file + ' does not exist in the expected directory')

