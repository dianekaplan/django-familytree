from django.core.management.base import BaseCommand
from ...models import Person, Family

class Command(BaseCommand):
    help = 'Populates direct_family_number values for migrated database (internal use)'

    # given a family, get specified spouse
    def get_family_spouse(self, family, type):
        if type=='wife':
            try:
                spouse = Person.objects.get(id=family.wife_id)
            except:
                print("wife not found")
        else:
            try:
                spouse = Person.objects.get(id=family.husband_id)
            except:
                print("husband not found")

        return spouse

    # given a person, get the family they grew up in
    def get_person_family(self, person):
        try:
            their_family = Family.objects.get(id=person.family_id)
        except:
            pass
        else:
            return their_family

    def set_family_value(self, family, value_to_set):
        if not family.direct_family_number:
            family.direct_family_number = value_to_set
            family.save()
            print("set value for " + family.display_name + ": " + str(family.direct_family_number))

    def check_and_set_family_of_parent(self, family, type, value):
        try:
            person = self.get_family_spouse(family, type)
        except:
            pass
        else:
            try:
                person_parent_family = self.get_person_family(person)
            except:
                print("no parent family for: " + person.display_name)
                pass
            else:
                if person_parent_family:
                    self.set_family_value(person_parent_family, value)
                    self.populate_next_family(person_parent_family, person_parent_family.direct_family_number)

    def populate_next_family(self, family, last_value):
        wife_family_will_get = last_value * 2
        husband_family_will_get = wife_family_will_get + 1
        self.check_and_set_family_of_parent(family, 'wife', wife_family_will_get)
        self.check_and_set_family_of_parent(family, 'husband', husband_family_will_get)

    def populate_family_number_values(self):
        current_family_value = 1
        first_family = Family.objects.get(id=17) # start with my family and then go back
        self.set_family_value(first_family, current_family_value)
        self.populate_next_family(first_family, current_family_value)

    def handle(self, *args, **options):
        print("CALLING populate_family_number_values")
        self.populate_family_number_values()



