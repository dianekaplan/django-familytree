from django.core.management.base import BaseCommand

from ...models import Family, Person

"""Context:
We assign unique numbers to each family, with one family as the 'root family'.
From there, we traverse back to the family each parent was born into, for example:
root family: 1
root family's wife's family: 2*1
root family's husband's family: 2*1 + 1
These numbers will only be applied to the 'direct' families, the ancestors of the root family.
"""


class Command(BaseCommand):
    help = "Populates direct_family_number values for migrated database (internal use)"

    def add_arguments(self, parser):
        parser.add_argument(
            "root family",
            type=int,
            help="root family to orient tree display",
        )

    # given a family, get specified spouse
    def get_family_spouse(self, family, type):
        if type == "wife":
            try:
                spouse = Person.objects.get(id=family.wife_id)
            except:
                print(f"Info: {family.display_name} family has no person set for wife")
        else:
            try:
                spouse = Person.objects.get(id=family.husband_id)
            except:
                print(f"Info: {family.display_name} family has no person set for husband")

        return spouse

    # given a person, get the family they grew up in
    def get_person_family(self, person):
        try:
            their_family = Family.objects.get(id=person.family.id)
        except:
            pass
        else:
            return their_family

    def set_family_value(self, family, value_to_set):
        if not family.direct_family_number:
            family.direct_family_number = value_to_set
            family.save()
            print(f"set value for {family.display_name}: {family.direct_family_number}")
        else:
            # Flag if we ever get a case where a record got a different value
            # than the script would assign
            if family.direct_family_number != value_to_set:
                print(
                    f"Family {family.display_name} has value {family.direct_family_number},"
                    f" but script would give {value_to_set}!"
                )

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
                    self.populate_next_family(
                        person_parent_family,
                        person_parent_family.direct_family_number,
                    )

    def populate_next_family(self, family, last_value):
        wife_family_will_get = last_value * 2
        husband_family_will_get = wife_family_will_get + 1
        self.check_and_set_family_of_parent(family, "wife", wife_family_will_get)
        self.check_and_set_family_of_parent(family, "husband", husband_family_will_get)

    def populate_family_number_values(self, root_family):
        # root family gets 1, then proceed back through parents
        starting_family_value = 1
        first_family = Family.objects.get(id=root_family)
        self.set_family_value(first_family, starting_family_value)
        self.populate_next_family(first_family, starting_family_value)

    def handle(self, *args, **kwargs):
        root_family = kwargs["root family"]
        print("CALLING populate_family_number_values")
        self.populate_family_number_values(root_family)
