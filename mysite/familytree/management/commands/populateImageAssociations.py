from django.core.management.base import BaseCommand, CommandError
from ...models import Person, Branch, Family, Image
from pathlib import Path
import csv

class Command(BaseCommand):
    help = 'Populates display names for migrated database (internal use)'

    def add_arguments(self, parser):
        parser.add_argument('image associations', type=Path, help='Image associations file')

    def add_image_branches(self):
        images = Image.objects.all()

        for image in images:
            if image.keem_line:
                branch_to_associate = Branch.objects.get(id=1)
                image.branches.add(branch_to_associate)
                image.save()
                print("Added " + branch_to_associate.display_name + " for: " + image.big_name)

            if image.husband_line:
                branch_to_associate = Branch.objects.get(id=2)
                image.branches.add(branch_to_associate)
                image.save()
                print("Added " + branch_to_associate.display_name + " for: " + image.big_name)

            if image.kemler_line:
                branch_to_associate = Branch.objects.get(id=3)
                image.branches.add(branch_to_associate)
                image.save()
                print("Added " + branch_to_associate.display_name + " for: " + image.big_name)

            if image.kaplan_line:
                branch_to_associate = Branch.objects.get(id=4)
                image.branches.add(branch_to_associate)
                image.save()
                print("Added " + branch_to_associate.display_name + " for: " + image.big_name)

    # An image can have an associated person OR family (or neither)- associate those
    def add_image_associations(self, file):
        with open(file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            next(reader) # skip the heading row
            for row in reader:
                    contents = (', '.join(row)).split(",")
                    image_id = int(contents[0])
                    person_value = contents[1]
                    family_value = contents[2]
                    image_to_update = Image.objects.get(id=image_id)

                    if person_value:
                        person_id = int(person_value)

                        if person_id > 0:
                            try:
                                person_to_associate = Person.objects.get(id=person_id)
                            except:
                                print(person_value + " doesn't match a person_id in our data")
                            image_to_update.person = person_to_associate
                            image_to_update.save()
                            print("associated " + person_to_associate.display_name + " with " + image_to_update.big_name)

                    if family_value:
                        family_id = int(family_value)

                        if family_id > 0:
                            try:
                                family_to_associate = Family.objects.get(id=family_id)
                            except:
                                print(family_value + " doesn't match a family_id in our data")
                            image_to_update.family = family_to_associate
                            image_to_update.save()
                            print("associated " + family_to_associate.display_name + " with " + image_to_update.big_name)

    def handle(self, *args, **kwargs):
        associations_file = kwargs['image associations']

        # validate that the user gave file with extension ged
        if associations_file.suffix!= '.csv':
            raise CommandError('Please specify image csv file, ex: images_people_family.csv')

        # Add branch associations to images
        self.add_image_branches()

        # Check that the files are there
        path = Path("familytree/management/commands/export_files/")
        path_plus_associations_file = path.joinpath(associations_file)

        # Add branch associations to images (uses file)
        if (path_plus_associations_file.is_file()):
            self.add_image_associations(path_plus_associations_file)
        else:
            raise CommandError(path_plus_associations_file + ' does not exist in the expected directory')

