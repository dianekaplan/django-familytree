from datetime import date

from django.core.management.base import BaseCommand

from ...models import Person


class Command(BaseCommand):
    help = "Populates/updates living bool: when needed " "(if value is empty or death info added since earlier value)"

    def handle(self, *args, **options):
        people = Person.objects.all()
        people_set_to_living_true = people.filter(living=True)
        people_set_to_living_false_without_death_data = (
            people.filter(living=False).filter(deathdate_note__isnull=True).filter(deathdate__isnull=True)
        )
        today = date.today()

        # Case #1: living value should be updated False->True (default not updated after creation)
        # Context: person records default to living = False upon creation (true for most ancestors)
        # @@TODO: confirm assumption: do we ever intentionally set value
        # to False with no deathdate info? (record like that would be
        # changed by this)

        print("People set to False who we'll update to True: ")
        for person in people_set_to_living_false_without_death_data:
            this_display_name = person.display_name

            # Check if birth year < 100 years ago
            qualifying_info = ""
            current_year_as_int = int(today.year)
            birthyear_as_int = 0

            if person.birthyear:
                birthyear_as_int = int(person.birthyear)
                if current_year_as_int - birthyear_as_int < 100:
                    qualifying_info = str(person.birthyear)

            elif person.birthdate:
                if today.year - person.birthdate.year < 100:
                    qualifying_info = str(person.birthdate)

            elif person.birthdate_note:
                if len(person.birthdate_note) == 4:
                    birthyear_as_int = int(person.birthdate_note)

                if len(person.birthdate_note) > 4:
                    this_value = person.birthdate_note
                    this_value = this_value.replace("abt ", "").replace("Abt. ", "")
                    if len(this_value) == 4:
                        birthyear_as_int = int(this_value)
                if current_year_as_int - birthyear_as_int < 100:
                    qualifying_info = person.birthdate_note

            if qualifying_info:
                print(this_display_name + ": " + qualifying_info)
                person.living = True
                person.save()

        # Case #2: living value should be updated True -> False
        # death fields have been populated, or 100 years since birth
        print("\nPeople set to true who we'll update to false " "(have death notes or 100 years since birth): ")
        current_year_as_int = int(today.year)
        for person in people_set_to_living_true:
            qualifying_info = ""
            this_display_name = person.display_name

            # set living to False if there's death information
            if person.deathdate_note or person.deathdate:
                qualifying_info = str(person.deathdate) if person.deathdate else person.deathdate_note

            # set living to False if birthyear value >=100 years ago
            elif person.birthyear:
                birthyear_as_int = int(person.birthyear)
                if current_year_as_int - birthyear_as_int >= 100:
                    qualifying_info = person.birthyear

            ## Rare cases below (I always populate birthyear when I have birthdate and/or note)
            # set living to False if birthdate value >=100 years ago
            elif person.birthdate:
                if current_year_as_int - person.birthdate.year >= 100:
                    qualifying_info += str(person.birthdate)

            # set living to False if birthdate_note contains year >=100 years ago
            elif person.birthdate_note:
                qualifying_info = ""
                birthyear_as_int = 0
                if len(person.birthdate_note) == 4:
                    birthyear_as_int = int(person.birthdate_note)
                    if current_year_as_int - birthyear_as_int >= 100:
                        qualifying_info = str(birthyear_as_int)

                elif len(person.birthdate_note) > 4:
                    this_value = person.birthdate_note
                    this_value = this_value.replace("abt ", "").replace("Abt. ", "")
                    if len(this_value) == 4:
                        birthyear_as_int = int(this_value)
                        if current_year_as_int - birthyear_as_int >= 100:
                            qualifying_info = str(birthyear_as_int)

            if qualifying_info:
                print(this_display_name + ": " + str(qualifying_info))
                person.living = False
                person.save()
