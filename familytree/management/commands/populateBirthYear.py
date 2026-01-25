import re

from django.core.management.base import BaseCommand

from ...models import Person


class Command(BaseCommand):
    help = "Populates birth year field for people (internal use)"

    def handle(self, *args, **options):
        people_without_birthyear = Person.objects.filter(birthyear__isnull=True)

        print("Populate birthyear value for people records where it's missing: ")
        for person in people_without_birthyear:
            # if birthdate is populated, grab it from there
            if person.birthdate:
                person.birthyear = person.birthdate.year
                person.save()
                print("Saved value using birthdate: " + str(person.birthdate) + ": " + str(person.birthyear))
                continue

            # if birthdate_note is populated, check the value for 4-digit chunks
            if person.birthdate_note:
                potential_year_matches = re.findall(r"\d{4}", person.birthdate_note)
                if potential_year_matches:
                    if len(potential_year_matches) < 2:
                        person.birthyear = int(potential_year_matches[0])
                        person.save()
                        print(
                            "Saved value using birthdate_note: " + person.birthdate_note + ": " + str(person.birthyear)
                        )
                    else:
                        print(
                            f"{person.display_name} birthdate_note has multiple potential matches "
                            f"to review: {potential_year_matches}"
                        )
                else:
                    print(
                        "This person has birthdate note but no birthyear saved: "
                        + person.display_name
                        + ": "
                        + person.birthdate_note
                    )
