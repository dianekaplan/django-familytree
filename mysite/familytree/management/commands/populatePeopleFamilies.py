from django.core.management.base import BaseCommand, CommandError
from ...models import Person, Family
from pathlib import Path
import csv

class Command(BaseCommand):
    help = 'Populate original family value for people (internal)'
    missing_args_message = 'Please specify file to use'
    gedcom_person_records = 0;
    gedcom_family_records = 0;
    person_added_count = 0;
    family_added_count = 0;
    person_skipped_count = 0;
    child_family_dict = {}

    def add_arguments(self, parser):
        parser.add_argument('file name', type=Path, help='Name of people/families file to use')


    def add_person_family(self, person_id, family_id):
        try:
            matching_person = Person.objects.get(id=person_id)
        except:
            print(person_id + " doesn't match a person_id in our data")

        try:
            matching_family = Family.objects.get(id=family_id)
        except:
            print(family_id + " doesn't match a family_id in our data")

        try:
            matching_person.family_id = matching_family
            matching_person.save()
            print("Added origin family for person: " + str(person_id))
        except:
            raise CommandError("Something went wrong for person: " + person_id)

    def handle(self, *args, **kwargs):
        filename = kwargs['file name']

        # validate that the user gave file with extension ged
        if filename.suffix!= '.csv':
            raise CommandError('Please specify csv file, ex: people_families.csv')

        # Check that the file is there
        path = Path("familytree/management/commands/export_files/")
        path_plus_file = path.joinpath(filename)

        if (path_plus_file.is_file()):
            with open(path_plus_file, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                next(reader) # skip the heading row
                for row in reader:
                    contents = (', '.join(row)).split(",")
                    person_id = int(contents[0])
                    family_value = contents[1]

                    if family_value:
                        family_id = int(family_value)

                        if family_id > 0:
                            self.add_person_family(person_id, family_id)
        else:
            raise CommandError('That file does not exist in the expected directory')
