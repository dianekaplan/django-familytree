from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from ...models import Person, Note, Family
import datetime
from django.conf import settings
from django.utils.timezone import make_aware


class Command(BaseCommand):
    help = 'Migrates notes and image_person data from previous database(internal use)'

    settings.TIME_ZONE


    def populate_notes(self):
        # Fetch the old data
        with connections['source'].cursor() as cursor:
            cursor.execute('select * from notes')
            data = cursor.fetchall()

        # Write it to your new models
        for note_row in data:
            print(note_row)
            row_list = list(note_row)

            parameters_dict = {'id':row_list[0], 'author_name':row_list[3],'body': row_list[4], 'date': row_list[5], 'active': True,
                               'for_self' : False,'created_at':make_aware(row_list[9]), 'updated_at' : make_aware(row_list[10])}

            if row_list[2]:
                try:
                    author = Person.objects.get(id=row_list[2])
                except:
                    print(str(row_list[2]) + " author doesn't match a person_id in our data")
                parameters_dict['author'] = author

            # The old schema used a 'type': value was 1 for person, 2 for family. This is the second item in the result array
            if row_list[1] == 1:
                try:
                    person_to_associate = Person.objects.get(id=row_list[6])
                    parameters_dict['person'] = person_to_associate
                except:
                    print(str(id=row_list[6]) + " doesn't match a person_id in our data")

            if row_list[1] == 2:
                try:
                    family_to_associate = Family.objects.get(id=row_list[6])
                    parameters_dict['family'] = family_to_associate
                except:
                    print(str(id=row_list[6]) + " doesn't match a family_id in our data")

            # save it to the new database (using 'default')
            (obj, created_bool) = Note.objects.using('default').get_or_create(**parameters_dict)
            print("making note: " + row_list[4])


    def handle(self, *args, **kwargs):
        self.populate_notes()
