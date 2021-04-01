from django.core.management.base import BaseCommand, CommandError
from gedcom.element.individual import IndividualElement
from gedcom.element.family import FamilyElement
from gedcom.parser import Parser
from ...models import Person, Family
from pathlib import Path
from django.utils import timezone

class Command(BaseCommand):
    help = 'Imports records from GEDCOM file'
    missing_args_message = 'Please specify GEDCOM file'
    gedcom_person_records = 0;
    gedcom_family_records = 0;
    person_added_count = 0;
    family_added_count = 0;
    person_skipped_count = 0;
    child_family_dict = {}

    def add_arguments(self, parser):
        parser.add_argument('file name', type=Path, help='Name of GEDCOM file to import from')

    def handle(self, *args, **kwargs):
        filename = kwargs['file name']

        # validate that the user gave file with extension ged
        if filename.suffix!= '.ged':
            raise CommandError('Please specify GEDCOM file, ex: myGedcom.ged')

        # Check that the file is there
        path = Path("familytree/management/commands/gedcom_files/") # @@TODO: update to take the whole path (so it doesn't need to be saved in a particular folder)
        path_plus_file = path.joinpath(filename)

        if (path_plus_file.is_file()):
            gedcom_parser = Parser()
            gedcom_parser.parse_file(path_plus_file)
            root_child_elements = gedcom_parser.get_root_child_elements()

            gedcom_parser.print_gedcom(path_plus_file)



            for element in root_child_elements:

                # gedcom_parser.print_gedcom()

                # find/add people records
                if isinstance(element, IndividualElement):
                    self.handle_person(element)

                # find/add family records (person records exist already, so we can look up parent references)
                # also save intermediate dictionary: CHIL INDI - family INDI
                if isinstance(element, FamilyElement):
                    self.handle_family(element)


        else:
            raise CommandError('That gedcom file does not exist in the expected directory')

        # # gather run results
        # run_results = 'gedcom_person_records: ' + str(self.gedcom_person_records) +  '\n'
        # run_results += 'gedcom_family_records: ' + str(self.gedcom_family_records) +  '\n'
        # run_results += 'person_added_count: ' + str(self.person_added_count) +  '\n'
        # run_results += 'person_skipped_count: ' + str(self.person_skipped_count) +  '\n'
        # run_results += 'family_added_count: ' + str(self.family_added_count) +  '\n'
        #
        # # Display and log them
        # self.stdout.write(self.style.SUCCESS('You passed filename: ') + str(filename))
        # self.stdout.write(run_results )
        # f = open('ImportInfo.txt', 'w')
        # f.write(run_results)
        # f.closed

    def handle_person(self, element):
        print("person element: " + str(element))

        # check the children for our custom UUID field (applicable for subsequent imports)
        element_children = element.get_child_elements()
        for child in element_children:
            print("child element: "+ str(child))


    def handle_family(self, element):
        print("family element: " + str(element))
        element_children = element.get_child_elements()


        for child in element_children:  # @TODO: look back at gedcom_parser.get_family_members approach: there you see FAMS but not wife vs husband
            # print(element.to_gedcom_string(recursive=True))
            print("child element: " + str(child))
