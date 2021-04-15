from django.core.management.base import BaseCommand, CommandError
from ...models import Person

class Command(BaseCommand):
    help = 'Populates birth year field for people (internal use)'

    def handle(self, *args, **options):
        people = Person.objects.all()

        print("Populate birthyear value for people records where it's missing: ")
        for person in people:
            birthyear_as_int = None
            this_display_name = ''
            if person.nickname:
                this_display_name = person.nickname.strip() + " " + person.last.strip()
            else:
                this_display_name = person.first.strip() + " " + person.last.strip()

            if not person.birthyear:
                print(this_display_name)
                if person.birthdate:
                    person.birthyear = person.birthdate.year
                    person.save()
                    print("Saved value using birthdate: " + str(person.birthdate) + ": " + str(person.birthyear))
                    continue

                if person.birthdate_note:
                    cleaned_value = person.birthdate_note.replace("?", "").replace("ish", "").replace(" ", "")
                    if len(cleaned_value) == 4:
                        birthyear_as_int = int(cleaned_value)

                    if len(cleaned_value) > 4:
                        birthyear_as_int = None
                        this_value = cleaned_value.replace("abt ", "").replace("Abt. ", "")
                        array = this_value.split("/")
                        if len(array) > 1:
                            year = array[len(array)-1]
                            if len(year) == 4:
                                birthyear_as_int = int(year)
                            if len(this_value) == 4:
                                birthyear_as_int = int(this_value)

                    if birthyear_as_int:
                        person.birthyear = birthyear_as_int
                        person.save()
                        print("Saved value using birthdate_note: " + person.birthdate_note + ": " + str(person.birthyear))
