from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from ...models import Person, Audiofile, Branch

import datetime
from django.conf import settings
from django.utils.timezone import make_aware


class Command(BaseCommand):
    help = 'Adds audio file records from previous database (internal use)'

    settings.TIME_ZONE

    def populate_audio_files(self):
        with connections['source'].cursor() as cursor:
            cursor.execute('select * from audiofiles')
            data = cursor.fetchall()

        # Write it to your new models
        for row in data:
            row_list = list(row)

            # make initial record
            parameters_dict = {'id': row_list[0],'filename':row_list[1],'summary': row_list[2], 'recording_date': row_list[3],
                               'created_at':make_aware(row_list[10]), 'updated_at' : make_aware(row_list[11])}

            (obj, created_bool) = Audiofile.objects.using('default').get_or_create(**parameters_dict)
            print("audio file record: " + str(row_list[1]))

            # add branch associations based on family bools
            keem_line = row_list[6]
            husband_line = row_list[7]
            kemler_line = row_list[8]
            kaplan_line = row_list[9]

            if keem_line:
                branch_to_associate = Branch.objects.get(id=1)
                obj.branches.add(branch_to_associate)
                obj.save()
                print("Added " + branch_to_associate.display_name + " for: " + obj.filename)

            if husband_line:
                branch_to_associate = Branch.objects.get(id=2)
                obj.branches.add(branch_to_associate)
                obj.save()
                print("Added " + branch_to_associate.display_name + " for: " + obj.filename)

            if kemler_line:
                branch_to_associate = Branch.objects.get(id=3)
                obj.branches.add(branch_to_associate)
                obj.save()
                print("Added " + branch_to_associate.display_name + " for: " + obj.filename)

            if kaplan_line:
                branch_to_associate = Branch.objects.get(id=4)
                obj.branches.add(branch_to_associate)
                obj.save()
                print("Added " + branch_to_associate.display_name + " for: " + obj.filename)

    def associate_people_with_audio_files(self):
        with connections['source'].cursor() as cursor:
            cursor.execute('select * from audiofile_person')
            data = cursor.fetchall()

            for row in data:
                try:
                    file_to_associate = Audiofile.objects.get(id=row[2])
                except:
                    print(str(row[2]) + "  doesn't match an audio file in our data")
                else:
                    try:
                        person_to_associate = Person.objects.get(id=row[1])
                    except:
                        print(str(row[1]) + "  doesn't match a person_id in our data")
                    else:
                        file_to_associate.person.add(person_to_associate)
                        file_to_associate.save()
                        print("added association for: " + person_to_associate.display_name + " and file:" + file_to_associate.filename)

    def handle(self, *args, **kwargs):
        print("ADDING audio file records")
        self.populate_audio_files()
        print("ADDING people/audio_file associations")
        self.associate_people_with_audio_files()
