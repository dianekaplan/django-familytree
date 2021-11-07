import dateutil.parser
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
    child_family_dict = {}  # map of gedcom child/family associations (eg. P7: F1)

    def add_arguments(self, parser):
        parser.add_argument('file name', type=Path, help='Name of GEDCOM file to import from')

    def handle(self, *args, **kwargs):
        filename = kwargs['file name']

        # validate that the user gave file with extension ged
        if filename.suffix!= '.ged':
            raise CommandError('Please specify GEDCOM file, ex: myGedcom.ged')

        # Check that the file is there
        path = Path("mysite/familytree/management/commands/gedcom_files/") # @@TODO: update to take the whole path (so it doesn't need to be saved in a particular folder)
        path_plus_file = path.joinpath(filename)

        if path_plus_file.is_file():
            gedcom_parser = Parser()
            gedcom_parser.parse_file(path_plus_file)
            root_child_elements = gedcom_parser.get_root_child_elements()

            # Find/add person records
            for element in root_child_elements:
                if isinstance(element, IndividualElement):
                    self.handle_person(element)

            # Find/add family records (after person records exist, so we can look up parents)
            # also save intermediate dictionary: CHIL INDI - family INDI
            for element in root_child_elements:
                if isinstance(element, FamilyElement):
                    self.handle_family(element)

            # now that we've saved all the people and families, populate orig_family on people records
            self.add_person_family_values(self.child_family_dict)

        else:
            raise CommandError('That gedcom file does not exist in the expected directory')

        # gather run results
        run_results = 'gedcom_person_records: ' + str(self.gedcom_person_records) + '\n'
        run_results += 'gedcom_family_records: ' + str(self.gedcom_family_records) + '\n'
        run_results += 'person_added_count: ' + str(self.person_added_count) + '\n'
        run_results += 'person_skipped_count: ' + str(self.person_skipped_count) + '\n'
        run_results += 'family_added_count: ' + str(self.family_added_count) + '\n'

        # Display and log them
        self.stdout.write(self.style.SUCCESS('You passed filename: ') + str(filename))
        self.stdout.write(run_results )
        f = open('ImportInfo.txt', 'w')
        f.write(run_results)
        f.closed

    # check a FACT to see if this is an AKA with a value matching a person record (unique ID)
    # return two things: matching person (or False), and uuid value from AKA FACT
    def check_fact_for_AKA(self, item, display_name, element):
        has_type_AKA = False
        matching_record = False
        gedcom_uuid = ''

        children = item.get_child_elements()
        for x in children:
            if "AKA" in str(x):
                has_type_AKA = True

        if has_type_AKA:
            gedcom_uuid = str(item).replace("1 FACT ", "").replace("\r\n", "").strip()
            try:
                matching_record = Person.objects.get(gedcom_uuid=gedcom_uuid)
            except Person.DoesNotExist:
                matching_record = False
                print("REVIEW: " + display_name + ": got AKA FACT value without matching person record: " , gedcom_uuid)
        return matching_record, gedcom_uuid


    # process a person record in the gedcom file
    def handle_person(self, element):
        matching_record = None
        self.gedcom_person_records += 1
        (gedcom_first_middle, last) = element.get_name()
        gedcom_uuid = ''
        skip_record = False

        # gather the data we'll want to use
        if "INDI" in str(element):
            gedcom_indi = str(element).replace(" INDI", "").replace("0 ", "").replace("\r\n", "")
        # get the fields available from our parser
        (birthdate, birthplace, sources) = element.get_birth_data()
        sex = element.get_gender()
        occupation = element.get_occupation()
        (deathdate, deathplace, sources) = element.get_death_data()
        display_name = gedcom_first_middle + " " + last
        element_children = element.get_child_elements()

        should_make_person = True
        for child in element_children:

            if "FACT" in str(child):
                matching_record, uuid_from_fact = self.check_fact_for_AKA(child, display_name, element)
                gedcom_uuid = uuid_from_fact

                if matching_record:
                    should_make_person = False
                    self.update_matching_person_record(matching_record, element, gedcom_indi)
                    self.person_skipped_count += 1
        if should_make_person:
                (obj, created_bool) = Person.objects.get_or_create(gedcom_indi=gedcom_indi, gedcom_uuid=gedcom_uuid,
                                                                       first=gedcom_first_middle, last=last,
                                                                       display_name=display_name, birthdate_note=birthdate,
                                                                       birthplace=birthplace, sex=sex, work=occupation,
                                                                       deathdate_note=deathdate, death_place=deathplace,
                                                                       show_on_landing_page=True,
                                                                       created_at=timezone.now(), updated_at = timezone.now(),
                                                                       reviewed=False)
                self.update_date_fields(obj)

                if created_bool:
                    self.person_added_count += 1


    # steps to process a family record in the gedcom file
    def handle_family(self, element):
        gedcom_indi = str(element).replace(" FAM", "").replace("0 ", "").replace("\r\n", "")
        self.gedcom_family_records += 1
        no_kids_bool = True
        wife = ""
        husband = ""
        element_children = element.get_child_elements()
        marriage_date = ""
        husband_indi= ""
        wife_indi = ""

        for child in element_children:  # @TODO: look back at gedcom_parser.get_family_members approach: there you see FAMS but not wife vs husband
            # print(element.to_gedcom_string(recursive=True))
            if "MARR" in str(child):
                marriage_info = child.get_child_elements()
                for item in marriage_info:
                    if "PLAC" in str(item):
                        marriage_place = str(item).replace("2 PLAC ", "")
                    if "DATE" in str(item):
                        marriage_date = str(item).replace("2 DATE ", "")
            if "WIFE" in str(child):
                wife_indi = str(child).replace("1 WIFE ", "").replace("\r\n", "")
                try:
                    this_person = Person.objects.get(gedcom_indi=wife_indi) #this person does not exist for our family @F118@
                    wife = this_person
                except:
                    print("For family " + gedcom_indi + ", couldn't find person matching wife_indi " + wife_indi)
            if "HUSB" in str(child):
                husband_indi = str(child).replace("1 HUSB ", "").replace("\r\n", "")
                try:
                    this_person = Person.objects.get(gedcom_indi=husband_indi)
                    husband = this_person
                except:
                    print("For family " + gedcom_indi + ", couldn't find person matching husband_indi " + husband_indi)
            if "CHIL" in str(child):
                no_kids_bool = False
                child_indi = str(child).replace("1 CHIL ", "").replace("\r\n",
                                                                       "")  # @FIXME: originally did += for text field, but if this works we won't need to use that text field
                if child_indi not in self.child_family_dict:
                    self.child_family_dict[child_indi] = gedcom_indi  # add dictionary entry for the child

        display_name = (wife.display_name + " & " if wife != "" else "(unknown name) & ")
        display_name += (husband.display_name if husband != "" else "(unknown name)")

        existing_record = self.find_existing_family_record(wife, husband)
        if not existing_record:
            (obj, created_bool) = Family.objects.get_or_create(gedcom_indi=gedcom_indi, display_name=display_name,
                                                               wife_indi=wife_indi, husband_indi=husband_indi,
                                                               marriage_date_note=marriage_date, no_kids_bool=no_kids_bool,
                                                               created_at = timezone.now(), updated_at = timezone.now(), reviewed=False)

            # link the parents that are known
            if wife != "":
                obj.wife = wife
                obj.save()
            if husband != "":
                obj.husband = husband
                obj.save()

            if created_bool:
                self.family_added_count += 1
        else:
            existing_record.gedcom_indi = gedcom_indi
            existing_record.save()

    # Loop through dictionary
    def add_person_family_values(self, child_family_dict):
        for entry in self.child_family_dict:
            try:
                this_person = Person.objects.get(gedcom_indi=entry)
            except:
                print("Gedcom file had child/family association where we didn't find person: " + entry + " " + child_family_dict.get(entry))
            try:
                orig_family = Family.objects.get(gedcom_indi=self.child_family_dict.get(entry))
            except:
                print("REVIEW: check family for " + str(entry))
                print("Gedcom file had child/family association where we didn't find family: " + self.child_family_dict.get(entry))
            else:
                this_person.family = orig_family
                this_person.save()


    # If we have a matching person record already, just update relevant fields
    # @TODO: consider fields we may want to populate if blank in our record (e.g. birthdate)
    def update_matching_person_record(self, matching_record, element, gedcom_indi):
        print("(Existing person, only update gedcom_indi: " + matching_record.first + " " +  matching_record.last + ")")

        matching_record.gedcom_indi = gedcom_indi
        matching_record.save()


    # gedcom files only need one parent and one child  @TODO: add support for one parent/child
    def find_existing_family_record(self, wife, husband):
        existing_family_record = None
        if wife and husband:
            try:
                existing_family_record = Family.objects.filter(wife=wife, husband=husband)
            except:
                return None

            if existing_family_record.count() > 1:
                print("REVIEW: Multiple family records found for : " + husband.first + " " + wife.first)
                for family in existing_family_record:
                    print (family.display_name)
                    return existing_family_record
            else:
                try:
                    existing_family_record = Family.objects.get(wife=wife, husband=husband)
                except:
                    pass
                else:
                    return existing_family_record

    # If 'note' date string is long enough and has all three parts, parse it
    def make_string_from_date(self, date_string):
        array = date_string.split(" ")
        if len(array) < 3:
            return None

        if len(date_string) < 10:
            return None

        else:
            result = ''
            try:
                result = dateutil.parser.parse(date_string)
            finally:
                return result

    def update_date_fields(self, obj):
        birthdate_result = self.make_string_from_date(obj.birthdate_note)
        deathdate_result = self.make_string_from_date(obj.deathdate_note)

        if birthdate_result:
            obj.birthdate = birthdate_result

        if deathdate_result:
            obj.deathdate = deathdate_result
        obj.save()
