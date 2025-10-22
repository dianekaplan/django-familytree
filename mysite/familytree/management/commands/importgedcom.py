from pathlib import Path

import dateutil.parser
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from gedcom.element.family import FamilyElement
from gedcom.element.individual import IndividualElement
from gedcom.parser import Parser

from ...models import Family, Person


class Command(BaseCommand):
    help = "Imports records from GEDCOM file"
    missing_args_message = "Please specify GEDCOM file"
    gedcom_person_records = 0
    gedcom_family_records = 0
    person_added_count = 0
    family_added_count = 0
    person_skipped_count = 0
    child_family_dict = {}  # map of gedcom child/family associations (eg. P7: F1)
    unique_id_list = []

    gedcom_data_path = Path(
        "mysite/familytree/management/commands/gedcom_files/"
    )  # @@TODO: update to take the whole path (so it doesn't need to be saved in a particular folder)

    path_plus_person_skip_file = gedcom_data_path.joinpath("person_skip_list.txt")
    person_skip_list = []

    try:
        with open(path_plus_person_skip_file, "r") as file:
            lines = file.readlines()
            person_skip_list = [line.strip() for line in lines]
    except:
        pass

    def add_arguments(self, parser):
        parser.add_argument("file name", type=Path, help="Name of GEDCOM file to import from")

    def handle(self, *args, **kwargs):
        filename = kwargs["file name"]

        # validate that the user gave file with extension ged
        if filename.suffix != ".ged":
            raise CommandError("Please specify GEDCOM file, ex: myGedcom.ged")

        # Check that the file is there
        path_plus_gedcom_file = self.gedcom_data_path.joinpath(filename)

        if path_plus_gedcom_file.is_file():
            gedcom_parser = Parser()
            gedcom_parser.parse_file(path_plus_gedcom_file)
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

            # Now that we've saved all the people and families, populate orig_family on people records
            self.add_person_family_values(self.child_family_dict)

        else:
            raise CommandError("That gedcom file does not exist in the expected directory")

        # gather run results
        run_results = "gedcom_person_records: " + str(self.gedcom_person_records) + "\n"
        run_results += "gedcom_family_records: " + str(self.gedcom_family_records) + "\n"
        run_results += "person_added_count: " + str(self.person_added_count) + "\n"
        run_results += "person_skipped_count: " + str(self.person_skipped_count) + "\n"
        run_results += "family_added_count: " + str(self.family_added_count) + "\n"

        # Display and log them
        self.stdout.write(self.style.SUCCESS("You passed filename: ") + str(filename))
        self.stdout.write(run_results)
        f = open("ImportInfo.txt", "w")
        f.write(run_results)
        f.closed

    # check a FACT to see if this is an AKA with a value matching a person record (unique ID)
    # return two things: matching person (or False), and uuid value from AKA FACT
    def check_fact_for_AKA(self, item, display_name, element):
        has_type_AKA = False
        matching_record = False
        gedcom_uuid = ""

        children = item.get_child_elements()
        for x in children:
            if "AKA" in str(x):
                has_type_AKA = True

        if has_type_AKA:
            for x in children:
                if "NOTE" in str(x):
                    gedcom_uuid = str(x).replace("2 NOTE ", "").replace("\r\n", "").strip()

            # gedcom_uuid = str(item).replace("1 FACT ", "").replace("\r\n", "").strip()
            try:
                matching_records = Person.objects.filter(gedcom_uuid=gedcom_uuid)
                if matching_records.count() > 1:
                    print(f"ATTENTION!! MULTIPLE DATABASE RECORDS HAVE SAME UNIQUE ID: {gedcom_uuid}")
                matching_record = matching_records.first()
            except Person.DoesNotExist:
                matching_record = False
                print(
                    "REVIEW: " + display_name + ": got AKA FACT value without matching person record: ",
                    gedcom_uuid,
                )
        return matching_record, gedcom_uuid

    # Process a person record in the gedcom file
    def handle_person(self, element):
        matching_record = None
        self.gedcom_person_records += 1
        (gedcom_first_middle, last) = element.get_name()
        gedcom_uuid = ""

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

        skip_record = False

        if display_name.strip() in self.person_skip_list:
            skip_record = True
            print(f"Skipping record matching person_skip_list: {display_name}")
        else:
            for child in element_children:
                if "FACT" in str(child):
                    matching_record, uuid_from_fact = self.check_fact_for_AKA(child, display_name, element)
                    gedcom_uuid = uuid_from_fact
                    if gedcom_uuid in self.unique_id_list:
                        print(f"GEDCOM FILE HAS REPEATED UNIQUE ID: {gedcom_uuid}, SKIPPING PERSON")
                    else:
                        self.unique_id_list.append(gedcom_uuid)
                        if matching_record:
                            skip_record = True
                            self.update_matching_person_record(matching_record, element, gedcom_indi)

        if skip_record:
            self.person_skipped_count += 1
        else:
            (obj, created_bool) = Person.objects.get_or_create(
                gedcom_indi=gedcom_indi,
                gedcom_uuid=gedcom_uuid,
                first=gedcom_first_middle,
                last=last,
                display_name=display_name,
                birthdate_note=birthdate,
                birthplace=birthplace,
                sex=sex,
                work=occupation,
                deathdate_note=deathdate,
                death_place=deathplace,
                show_on_landing_page=True,
                created_at=timezone.now(),
                updated_at=timezone.now(),
                reviewed=False,
            )
            self.update_date_fields(obj)

            if created_bool:
                self.person_added_count += 1

    # Steps to process a family record in the gedcom file
    # Summary: update/add a record if the WIFE and HUSB entries match person records in our database
    # (This can include newly-imported people; the ancestry.com GEDCOM export lists person records before family)
    def handle_family(self, element):
        gedcom_indi = str(element).replace(" FAM", "").replace("0 ", "").replace("\r\n", "")
        self.gedcom_family_records += 1
        no_kids_bool = True
        person_with_wife_indi = ""
        person_with_husband_indi = ""
        element_children = element.get_child_elements()
        marriage_date = ""
        husband_indi = ""
        wife_indi = ""

        # Gather family values from the child elements
        for child in (
            element_children
        ):  # @TODO: look back at gedcom_parser.get_family_members approach: there you see FAMS but not wife vs husband
            # print(element.to_gedcom_string(recursive=True))
            # if "MARR" in str(child):
            # marriage_info = child.get_child_elements()
            # @@FIXME revisit actually using these
            # for item in marriage_info:
            #     if "PLAC" in str(item):
            #         marriage_place = str(item).replace("2 PLAC ", "")
            #     if "DATE" in str(item):
            #         marriage_date = str(item).replace("2 DATE ", "")
            if "WIFE" in str(child):
                wife_indi = str(child).replace("1 WIFE ", "").replace("\r\n", "")
                try:
                    this_person = Person.objects.get(gedcom_indi=wife_indi)
                    person_with_wife_indi = this_person
                except:
                    pass
            if "HUSB" in str(child):
                husband_indi = str(child).replace("1 HUSB ", "").replace("\r\n", "")
                try:
                    this_person = Person.objects.get(gedcom_indi=husband_indi)
                    person_with_husband_indi = this_person
                except:
                    pass
            if "CHIL" in str(child):
                no_kids_bool = False
                child_indi = (
                    str(child).replace("1 CHIL ", "").replace("\r\n", "")
                )  # originally did += for text field, but if this works we won't need to use that text field
                try:
                    this_person = Person.objects.get(gedcom_indi=child_indi)
                except:
                    continue
                if child_indi not in self.child_family_dict:
                    self.child_family_dict[child_indi] = gedcom_indi  # add dictionary entry if existing person

        # Process the family record if it matches with two people in our database
        if person_with_wife_indi and person_with_husband_indi:
            display_name = person_with_wife_indi.display_name + " & " + person_with_husband_indi.display_name
            given_spouses_existing_record = self.find_existing_family_record(
                person_with_wife_indi, person_with_husband_indi
            )
            spouses_swapped_existing_record = self.find_existing_family_record(
                person_with_husband_indi, person_with_wife_indi
            )
            existing_family_record = given_spouses_existing_record or spouses_swapped_existing_record

            if existing_family_record:
                existing_family_record.gedcom_indi = gedcom_indi
                existing_family_record.wife_indi = wife_indi
                existing_family_record.husband_indi = husband_indi
                existing_family_record.save()
            else:
                # create a family record for these two people
                (obj, created_bool) = Family.objects.get_or_create(
                    gedcom_indi=gedcom_indi,
                    display_name=display_name,
                    wife_indi=wife_indi,
                    husband_indi=husband_indi,
                    marriage_date_note=marriage_date,
                    no_kids_bool=no_kids_bool,
                    created_at=timezone.now(),
                    updated_at=timezone.now(),
                    reviewed=False,
                )

                # link the associated parents
                obj.wife = person_with_wife_indi
                obj.husband = person_with_husband_indi
                obj.save()

                if created_bool:
                    self.family_added_count += 1

    # Loop through dictionary
    def add_person_family_values(self, child_family_dict):
        for entry in self.child_family_dict:
            try:
                this_person = Person.objects.get(gedcom_indi=entry)
            except:
                print(f"Gedcom file had child/family association where we didn't find person: {entry}")
                # {child_family_dict.get(entry)}")
            try:
                orig_family = Family.objects.get(gedcom_indi=self.child_family_dict.get(entry))
            except:
                # Ex: person is a child in gedcom family record with one parent (we only process those with two parents)
                print(f"REVIEW: for person {str(entry)} we didn't find family: {self.child_family_dict.get(entry)}")
            if this_person and orig_family:
                this_person.family = orig_family
                this_person.save()

    # If we have a matching person record already, just update relevant fields
    # @@TODO: consider fields we may want to populate if blank in our record (e.g. birthdate)
    def update_matching_person_record(self, matching_record, element, gedcom_indi):
        # print(
        #     "(Existing person, only update gedcom_indi: "
        #     + matching_record.first
        #     + " "
        #     + matching_record.last
        #     + ")"
        # )
        # these gedcom_indi values link people to families in the file
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
                    print(family.display_name)
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
            result = ""
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
