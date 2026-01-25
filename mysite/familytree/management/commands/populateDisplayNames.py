from django.core.management.base import BaseCommand

from ...models import Person


class Command(BaseCommand):
    help = "Populates display names for migrated database (internal use)"

    def handle(self, *args, **options):

        people = Person.objects.all()

        for person in people:
            this_display_name = ""
            if person.nickname:
                this_display_name = person.nickname.strip() + " " + person.last.strip()
            else:
                this_display_name = person.first.strip() + " " + person.last.strip()

            print(this_display_name)
            person.display_name = this_display_name
            person.save()
