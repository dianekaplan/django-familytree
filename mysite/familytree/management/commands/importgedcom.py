from django.core.management.base import BaseCommand, CommandError
from gedcom.element.individual import IndividualElement
from gedcom.element.family import FamilyElement
from gedcom.parser import Parser
from ...models import Person, Family
from pathlib import Path

class Command(BaseCommand):
    help = 'Imports records from GEDCOM file'
    missing_args_message = 'Please specify GEDCOM file'

    def add_arguments(self, parser):
        parser.add_argument('file name', type=Path, help='Name of GEDCOM file to import from')

    def handle(self, *args, **kwargs):
        filename = kwargs['file name']
        gedcom_person_records = 0;
        gedcom_family_records = 0;
        person_added_count = 0;
        family_added_count = 0;

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

            for element in root_child_elements:

                # find/add any person record as a person
                if isinstance(element, IndividualElement):
                    gedcom_person_records += 1
                    (gedcom_first_middle, last) = element.get_name()
                    gedcom_UUID = ''

                    if "INDI" in str(element):
                        gedcom_indi = str(element).replace(" INDI", "").replace("0 ", "")
                    # get the fields available from our parser
                    (birthdate, birthplace, sources) = element.get_birth_data()
                    sex = element.get_gender()
                    occupation = element.get_occupation()
                    (deathdate, deathplace, sources) = element.get_death_data()
                    display_name = gedcom_first_middle + " " + last

                    # check the children for our custom UUID field
                    element_children = element.get_child_elements()
                    for child in element_children:
                       # print(element.to_gedcom_string(recursive=True))
                        if "ALIA" in str(child):
                            gedcom_UUID = str(child).replace("1 ALIA ", "")

                    (obj, created_bool) = Person.objects.get_or_create(gedcom_indi = gedcom_indi, gedcom_UUID = gedcom_UUID, first_name=gedcom_first_middle, last_name=last, display_name=display_name, dob_string = birthdate, dob_place=birthplace, sex=sex, occupation=occupation, death_date_note=deathdate, death_place=deathplace)
                    if created_bool:
                        person_added_count += 1

                    person_info = gedcom_first_middle + " " + last + " gedcom_UUID: " + gedcom_UUID + "birthday info: " + birthdate + " " + birthplace + "\t sex: " + sex + " occupation: " + occupation + " Death info: " + deathdate, deathplace, sources
                    print(person_info)

                # find/add any family record as a family
                if isinstance(element, FamilyElement):
                    gedcom_indi = str(element).replace(" FAM", "").replace("0 ", "")
                    gedcom_family_records += 1
                    no_kids_bool = True
                    child_indi = ""
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
                        if "WIFE" in str(child):
                            wife_indi = str(child).replace("1 WIFE ", "")
                        if "HUSB" in str(child):
                            husband_indi = str(child).replace("1 HUSB ", "")
                        if "CHIL" in str(child):
                           no_kids_bool = False
                           child_indi += str(child).replace("1 CHIL ", "").replace("\r\n", "")

                    display_name = wife_indi + " & " + husband_indi
                    (obj, created_bool) = Family.objects.get_or_create(gedcom_indi=gedcom_indi, display_name = display_name,
                                                                       wife_indi=wife_indi, husband_indi=husband_indi,
                                                                       marriage_date_string=marriage_date, no_kids = no_kids_bool,
                                                                       child_indi = child_indi)
                    if created_bool:
                        family_added_count += 1

        else:
            raise CommandError('That gedcom file does not exist in the expected directory')

        # gather run results
        run_results = 'gedcom_person_records: ' + str(gedcom_person_records) +  '\n'
        run_results += 'gedcom_family_records: ' + str(gedcom_family_records) +  '\n'
        run_results += 'person_added_count: ' + str(person_added_count) +  '\n'
        run_results += 'family_added_count: ' + str(family_added_count) +  '\n'

        # Display and log them
        self.stdout.write(self.style.SUCCESS('You passed filename: ') + str(filename))
        self.stdout.write(run_results )
        f = open('ImportInfo.txt', 'w')
        f.write(run_results)
        f.closed


