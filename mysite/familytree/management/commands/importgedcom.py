from django.core.management.base import BaseCommand, CommandError
from gedcom.element.individual import IndividualElement
from gedcom.element.family import FamilyElement
from gedcom.parser import Parser

#from ...models import Person, Family
from pathlib import Path

from sys import stdout
class Command(BaseCommand):
    help = 'Imports records from GEDCOM file'
    missing_args_message = 'Please specify GEDCOM file'

    def add_arguments(self, parser):
        parser.add_argument('file name', type=Path, help='Name of GEDCOM file to import from')

    def handle(self, *args, **kwargs):
        filename = kwargs['file name']
        #filename = Path("Test_tree.ged") # @@TODO: take this out when you learn to properly add configuration

        # validate that the user gave file with extension ged
        if filename.suffix!= '.ged':
            raise CommandError('Please specify GEDCOM file, ex: myGedcom.ged')

        # Check that the file is there
        path = Path("familytree/management/commands/gedcom_files/")
        path_plus_file = path.joinpath(filename)

        if (path_plus_file.is_file()):
            file_contents = path_plus_file.read_text()


            gedcom_parser = Parser()  # Initialize the parser
            gedcom_parser.parse_file(path_plus_file) # Parse your file
            root_child_elements = gedcom_parser.get_root_child_elements()

            # Iterate through all root child elements
            for element in root_child_elements:

                # Is the `element` an actual `IndividualElement`? (Allows usage of extra functions such as `surname_match` and `get_name`.)
                if isinstance(element, IndividualElement):

                    # Get all individuals whose surname matches "Doe"
                    #if element.surname_match('Kaplan'):
                        # Unpack the name tuple
                        (gedcom_first_middle, last) = element.get_name()

                        (birthdate, birthplace, sources) = element.get_birth_data()
                        sex = element.get_gender()
                        occupation = element.get_occupation()
                        (deathdate, deathplace, sources) = element.get_death_data()

                        person_info = gedcom_first_middle + " " + last + "\t" + "birthday info: " + birthdate + " " + birthplace + "\t sex: " + sex + " occupation: " + occupation + " Death info: " + deathdate, deathplace, sources
                        print(person_info)

                        #Person.objects.create()
                        #print(element.to_gedcom_string(recursive=True))


                if isinstance(element, FamilyElement):
                    element_children = element.get_child_elements()
                    for child in element_children:
                        print(element.to_gedcom_string(recursive=True))
                        if "MARR" in str(child):
                            marriage_info = child.get_child_elements()
                            for item in marriage_info:
                                if "PLAC" in str(item):
                                    marriage_place = str(item).replace("2 PLAC ", "")
                                if "DATE" in str(item):
                                    marriage_date = str(item).replace("2 DATE ", "")
                            print( marriage_date + marriage_place)

        else:
            raise CommandError('That gedcom file does not exist in the expected directory')

        # read in the file

        # then I want to parse the file and do things with it


        # for poll_id in options['poll_ids']:
        #     try:
        #         poll = Poll.objects.get(pk=poll_id)
        #     except Poll.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)
        #
        #     poll.opened = False
        #     poll.save()

        self.stdout.write(self.style.SUCCESS('You passed filename: ') + str(filename))
        #self.stdout.write(Path('path_plus_file.name: ' + str(path_plus_file)))

