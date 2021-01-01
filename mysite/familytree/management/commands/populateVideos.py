from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from ...models import Person, Family, Branch, Video
import datetime
from django.conf import settings
from django.utils.timezone import make_aware


class Command(BaseCommand):
    help = 'Adds video records from previous database (internal use)'

    settings.TIME_ZONE

    def populate_videos(self):
        # Fetch the video data
        with connections['source'].cursor() as cursor:
            cursor.execute('select * from videos')
            data = cursor.fetchall()

        # Write it to your new models
        for video_row in data:
            print(video_row)
            row_list = list(video_row)

            # make initial video record
            parameters_dict = {'id': row_list[0],'name':row_list[1],'caption': row_list[2], 'year': row_list[3],
                               'created_at':make_aware(row_list[10]), 'updated_at' : make_aware(row_list[11])}

            (obj, created_bool) = Video.objects.using('default').get_or_create(**parameters_dict)
            print("video record: " + str(row_list[1]))


            # add branch associations based on family bools
            keem_line = row_list[6]
            husband_line = row_list[7]
            kemler_line = row_list[8]
            kaplan_line = row_list[9]

            if keem_line:
                branch_to_associate = Branch.objects.get(id=1)
                obj.branches.add(branch_to_associate)
                obj.save()
                print("Added " + branch_to_associate.display_name + " for: " + obj.name)

            if husband_line:
                branch_to_associate = Branch.objects.get(id=2)
                obj.branches.add(branch_to_associate)
                obj.save()
                print("Added " + branch_to_associate.display_name + " for: " + obj.name)

            if kemler_line:
                branch_to_associate = Branch.objects.get(id=3)
                obj.branches.add(branch_to_associate)
                obj.save()
                print("Added " + branch_to_associate.display_name + " for: " + obj.name)

            if kaplan_line:
                branch_to_associate = Branch.objects.get(id=4)
                obj.branches.add(branch_to_associate)
                obj.save()
                print("Added " + branch_to_associate.display_name + " for: " + obj.name)

    def associate_people_with_videos(self):
        with connections['source'].cursor() as cursor:
            cursor.execute('select * from person_video')
            data = cursor.fetchall()
            # look for any matching person_video records, and add person

            for row in data:
                print(row)

                try:
                    video_to_associate = Video.objects.get(id=row[2])
                    print("this is video: " + video_to_associate.name)
                except:
                    print(str(row[2]) + "  doesn't match a video_id in our data")
                else:
                    try:
                        person_to_associate = Person.objects.get(id=row[1])
                        print("person_to_associate: " + person_to_associate.display_name)
                    except:
                        print(str(row[1]) + "  doesn't match a person_id in our data")
                    else:
                        video_to_associate.person.add(person_to_associate)
                        video_to_associate.save()

    def handle(self, *args, **kwargs):
        print("ADDING video records")
        self.populate_videos()
        print("ADDING people/video associations")
        self.associate_people_with_videos()
