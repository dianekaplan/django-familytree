from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db.models.functions import Length

from ...models import Family, Person

"""Context: we assign unique ids to each person, based on the direct family numbers, like so:
1. Populate downward from direct families and their kids.
Ex: kids of a direct family will be simple (2Debbie, 2DebbieDanny, 1LarryViolet)
Cousins of people in direct families will have direct family number + S + firstname (12EttaSonnyDavid)

2. Populate outward to spouses (adding SP then name).
Ex: 1DianeSPChris, then 1DianeSPChrisIain, and Sarah: 1DianeSPChrisSPSarah.
If multiple marriages, increment SP (Ex. Elaine is 6StanleySP3, Melissa is 6StanleySP3KMelissa).
Parent of person notated by P (Ex. Elaine's mom: 6StanleySP3PKathryn)

3. Populate outward to siblings (adding S then name). Ex: Linda: 3ElaineSPSLinda
"""


class Command(BaseCommand):
    help = "Populates unique IDs for person records without one"

    # given a person, get the families that they're a spouse in
    def get_person_families(self, person):
        their_families = Family.objects.all().filter(Q(wife=person) | Q(husband=person)).order_by("id")
        return their_families

    # given a family, get the two spouses
    def get_family_spouses(self, family):
        spouses = Person.objects.filter(Q(id=family.wife_id) | Q(id=family.husband_id)).order_by("id")
        return spouses

    # given a family, get the kids
    def get_family_kids(self, family):
        kids = Person.objects.filter(family_id=family).order_by("id")
        return kids

    def populate_children_values(self, person):
        # grab all families where this person is a spouse
        families = Family.objects.all().filter(Q(wife=person) | Q(husband=person))
        for family in families:
            # grab all children in that family
            children = Person.objects.all().filter(family_id=family.id)
            child_names = []  # Handle case of same-named siblings (facepalm)
            repeat_seq = 0
            for child in children:
                firstname_cleaned = child.first.replace(" ", "_").replace("/", "_")
                if firstname_cleaned not in child_names:
                    child_names.append(firstname_cleaned)
                else:  # family has same-named siblings
                    firstname_cleaned = firstname_cleaned + str(repeat_seq)
                    repeat_seq += 1
                value_to_use = person.gedcom_uuid + firstname_cleaned

                if not child.gedcom_uuid:
                    child.gedcom_uuid = value_to_use
                    child.save()
                    print("set value for " + child.display_name + ": " + value_to_use)
                self.populate_children_values(child)

    def populate_downward_from_families(self):
        # grab all family objects where direct_family_number is populated
        families = Family.objects.filter(direct_family_number__isnull=False).order_by("direct_family_number")
        for family in families:
            children = Person.objects.all().filter(family_id=family.id)
            for person in children:
                if not person.gedcom_uuid:
                    gedcom_uuid = str(family.direct_family_number) + person.first.replace(" ", "_")
                    person.gedcom_uuid = gedcom_uuid
                    person.save()
                    print("set value for " + person.display_name + ": " + gedcom_uuid)
                self.populate_children_values(person)

    def populate_outward_to_spouses(self):
        # grab the people with gedcom_uuid populated
        populated_people = Person.objects.annotate(text_len=Length("gedcom_uuid")).filter(text_len__gt=0)
        for person in populated_people:
            their_families = self.get_person_families(person)
            spouse_count = 1

            for family in their_families:
                # grab that family's spouse who isn't the person we started with
                spouses = self.get_family_spouses(family)
                for spouse in spouses:
                    if spouse != person and not spouse.gedcom_uuid:
                        value_to_use_for_spouse = person.gedcom_uuid + "SP" + str(spouse_count) + spouse.first
                        spouse.gedcom_uuid = value_to_use_for_spouse
                        spouse.save()
                        print("set value for " + spouse.display_name + ": " + spouse.gedcom_uuid)
                spouse_count += 1

    def populate_outward_to_siblings(self):  # test with Linda Dolph
        # grab the people with gedcom_uuid populated
        populated_people = Person.objects.filter(gedcom_uuid__isnull=False)
        for person in populated_people:
            # grab their origin family (if they have one)
            try:
                origin_family = Family.objects.get(id=person.family_id_id)
            except:
                pass
            else:
                # get all kids of that family
                kids = self.get_family_kids(origin_family)

                # for kids beside the original person, populate their value if missing
                for kid in kids:
                    if kid != person and not kid.gedcom_uuid:
                        gedcom_uuid = person.gedcom_uuid + "S" + kid.first.replace(" ", "_")
                        kid.gedcom_uuid = gedcom_uuid
                        kid.save()
                        print("set value for " + kid.display_name + ": " + kid.gedcom_uuid)

    def check_if_in_direct_family(self, person):
        origin_family = None
        try:
            origin_family = Family.objects.get(id=person.family_id)
        except:
            pass
        else:
            if origin_family and origin_family.direct_family_number:
                value_to_use = str(origin_family.direct_family_number) + person.first.replace(" ", "_")
                person.gedcom_uuid = value_to_use
                person.save()
                print("Set value for " + person.display_name + ": " + person.gedcom_uuid)
                # @TODO: add support for the same-named sibling case, or validate first

    def check_parent_for_value(self, person):
        try:
            origin_family = Family.objects.get(id=person.family_id)
        except:
            pass
        else:
            parents = self.get_family_spouses(origin_family)
            for parent in parents:
                if parent.gedcom_uuid and not person.gedcom_uuid:  # only fill it in when it's still missing
                    value_for_kid = parent.gedcom_uuid + person.first.replace(" ", "_")
                    # @TODO: add support for the same-named sibling case, or validate first
                    person.gedcom_uuid = value_for_kid
                    person.save()
                    print("set value for " + person.display_name + ": " + person.gedcom_uuid)

    def check_spouse_for_value(self, person):
        try:
            person_families = self.get_person_families(person)
        except:
            pass
        else:
            for family in person_families:
                spouse_pair = self.get_family_spouses(family)
                for spouse in spouse_pair:
                    if spouse.gedcom_uuid:
                        person.gedcom_uuid = spouse.gedcom_uuid + "SP" + person.first.replace(" ", "_")
                        person.save()
                        print("set value for " + person.display_name + ": " + person.gedcom_uuid)

    def check_sibling_for_value(self, person):
        try:
            origin_family = Family.objects.get(id=person.family_id)
        except:
            pass
        else:
            siblings = self.get_family_kids(origin_family)
            for kid in siblings:
                if kid.gedcom_uuid and not person.gedcom_uuid:  # only fill it in when it's still missing
                    value_to_use = kid.gedcom_uuid + "S" + person.first.replace(" ", "_")
                    person.gedcom_uuid = value_to_use
                    person.save()
                    print("set value for " + person.display_name + ": " + person.gedcom_uuid)

    def check_kid_for_value(self, person):
        try:
            families = self.get_person_families(person)
        except:
            pass
        else:
            for family in families:
                kids = self.get_family_kids(family)
                for kid in kids:
                    if kid.gedcom_uuid and not person.gedcom_uuid:  # only fill it in when it's still missing
                        value_to_use = kid.gedcom_uuid + "P" + person.first.replace(" ", "_")
                        person.gedcom_uuid = value_to_use
                        person.save()
                        print("set value for " + person.display_name + ": " + person.gedcom_uuid)

    def populate_the_rest(self):  # kids of people who married in, then upward
        # grab the people with gedcom_uuid NOT populated
        people_missing_value = Person.objects.filter(gedcom_uuid__isnull=True)
        still_missing = 0
        for person in people_missing_value:
            self.check_if_in_direct_family(person)
            if not person.gedcom_uuid:  # (don't revisit if a previous step set it)
                self.check_parent_for_value(person)
            if not person.gedcom_uuid:
                self.check_kid_for_value(person)
            if not person.gedcom_uuid:
                self.check_spouse_for_value(person)
            if not person.gedcom_uuid:
                self.check_sibling_for_value(person)
            if not person.gedcom_uuid:
                print("still missing it for " + person.display_name)
                still_missing += 1
        print("Missing Gedcom uuid value for this many person records: " + str(still_missing))

    def handle(self, *args, **options):
        # This will only work if direct family numbers are already in place
        direct_families = Family.objects.filter(direct_family_number__isnull=False)
        if direct_families.count() < 1:
            print("Populate direct family numbers before running this script!")
            return

        person_records = Person.objects.all()
        people_missing_value = Person.objects.filter(gedcom_uuid__isnull=True)

        # If most records are unset, populate downward and outward
        if people_missing_value.count() / person_records.count() > 0.5:
            print("CALLING populate_downward_from_families")
            self.populate_downward_from_families()
            print("CALLING populate_outward_to_spouses")
            self.populate_outward_to_spouses()
            print("CALLING populate_outward_to_siblings")
            self.populate_outward_to_siblings()

        # If most records already have a value, we can run just this step (faster)
        print("CALLING populate_the_rest")
        self.populate_the_rest()
