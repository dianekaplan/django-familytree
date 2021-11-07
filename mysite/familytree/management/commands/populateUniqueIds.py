from django.core.management.base import BaseCommand
from ...models import Person, Family
from django.db.models import Q
from django.db.models.functions import Length


class Command(BaseCommand):
    help = 'Populates unique IDs for person records without one'

    # given a person, get the families that they're a spouse in
    def get_person_families(self, person):
        their_families = Family.objects.all().filter(Q(wife=person) | Q(husband=person)).order_by('id')
        return their_families

    # given a family, get the two spouses
    def get_family_spouses(self, family):
        spouses = Person.objects.filter(Q(id=family.wife_id) | Q(id=family.husband_id)).order_by('id')
        return spouses

    # given a family, get the kids
    def get_family_kids(self, family):
        kids = Person.objects.filter(family_id=family).order_by('id')
        return kids

    def populate_children_values(self, person):
        pass
        # grab all families where this person is a spouse
        families = Family.objects.all().filter(Q(wife=person) | Q(husband=person) )
        for family in families:
            # grab all children in that family
            children = Person.objects.all().filter(family_id=family.id)
            for child in children:
                if not child.gedcom_uuid:
                    gedcom_uuid = person.gedcom_uuid + child.first.replace(" ", "_").replace("/", "_")
                    child.gedcom_uuid = gedcom_uuid
                    child.save()
                    print("set value for " + child.display_name + ": " +gedcom_uuid)
                    self.populate_children_values(child)

    def populate_downward_from_families(self):
        # grab all family objects where gedcom_uuid is populated
        families = Family.objects.filter(direct_family_number__isnull=False).order_by('direct_family_number')
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
        populated_people = Person.objects.annotate(text_len=Length('gedcom_uuid')).filter(text_len__gt=0)
        for person in populated_people:
            their_families = self.get_person_families(person)
            spouse_count = 1

            for family in their_families:
                gedcom_uuid = person.gedcom_uuid + "SP"+ str(spouse_count)

                # it's safe to grab both spouses because we only update the one without a value already
                spouses = self.get_family_spouses(family)
                for spouse in spouses:
                    if not spouse.gedcom_uuid:
                        spouse.gedcom_uuid = gedcom_uuid
                        spouse.save()
                        print("set value for " + spouse.display_name + ": " + spouse.gedcom_uuid)
                spouse_count+=1

    def populate_outward_to_siblings(self): # Linda Dolph
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

                # for each kid, if their value is missing:
                for kid in kids:
                    if not kid.gedcom_uuid:
                        gedcom_uuid = person.gedcom_uuid + "S" + kid.first.replace(" ", "_")
                        kid.gedcom_uuid = gedcom_uuid
                        kid.save()
                        print("set value for " + kid.display_name + ": " + kid.gedcom_uuid)

    def check_parent_for_value(self, person):
        try:
            origin_family = Family.objects.get(id=person.family_id)
        except:
            pass
        else:
            parents = self.get_family_spouses(origin_family)
            for parent in parents:
                if parent.gedcom_uuid and not person.gedcom_uuid: # only fill it in when it's still missing
                    value_for_kid = parent.gedcom_uuid + person.first.replace(" ", "_")
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
        people_missing_value = Person.objects.annotate(text_len=Length('gedcom_uuid')).filter(text_len__lt=1)
        still_missing = 0
        for person in people_missing_value:
            self.check_spouse_for_value(person)
            if not person.gedcom_uuid:
                self.check_sibling_for_value(person)
            if not person.gedcom_uuid:
                self.check_kid_for_value(person)
            if not person.gedcom_uuid:
                self.check_parent_for_value(person)
            if not person.gedcom_uuid:
                print("still missing it for " + person.display_name)
                still_missing +=1
        print("missing value for this many: " + str(still_missing))

    def handle(self, *args, **options):
        print("CALLING populate_downward_from_families")
        self.populate_downward_from_families()
        print("CALLING populate_outward_to_spouses")
        self.populate_outward_to_spouses()
        print("CALLING populate_outward_to_siblings")
        self.populate_outward_to_siblings()
        print("CALLING populate_the_rest")
        self.populate_the_rest()


