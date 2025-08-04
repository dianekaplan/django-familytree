from datetime import date

from django.core.management.base import BaseCommand

from ...models import Person


class Command(BaseCommand):
    help = "Populates living bool: true if birth year within 100 years and deathdate fields are empty"

    def handle(self, *args, **options):
        people = Person.objects.all()
        today = date.today()

        print("People we know were born within 100 years (will set to living): ")
        for person in people:
            this_display_name = ""
            if person.nickname:
                this_display_name = person.nickname.strip() + " " + person.last.strip()
            else:
                this_display_name = person.first.strip() + " " + person.last.strip()

            if not person.deathdate_note and not person.deathdate:
                birthdate_info = ""
                current_year_as_int = int(today.year)
                birthyear_as_int = 0

                if person.birthdate_note:
                    if len(person.birthdate_note) == 4:
                        birthyear_as_int = int(person.birthdate_note)

                    if len(person.birthdate_note) > 4:
                        this_value = person.birthdate_note
                        this_value = this_value.replace("abt ", "").replace("Abt. ", "")
                        if len(this_value) == 4:
                            birthyear_as_int = int(this_value)

                    if current_year_as_int - birthyear_as_int < 100:
                        birthdate_info += person.birthdate_note

                if person.birthdate:
                    if today.year - person.birthdate.year < 100:
                        birthdate_info += str(person.birthdate)

                if birthdate_info:
                    print(this_display_name + ": " + birthdate_info)
                    person.living = True
                    person.save()
