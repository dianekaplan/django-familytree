from django.core.management.base import BaseCommand, CommandError
from ...models import Person, Image, ImagePerson, Family, Story, PersonStory, Login, User, FamilyStory, Video, VideoPerson
from django.db import connections
from pathlib import Path
import csv
from django.utils.timezone import make_aware

class Command(BaseCommand):
    help = 'Migrates data from identical tables from previous database (internal use)'

    def populate_image_person_rows(self):
        ported_data = ImagePerson.objects.using('source').all()

        for row in ported_data:
            try:
                person_to_associate = Person.objects.get(id=row.person_id)
            except:
                print(str(row.person_id) + " doesn't match a person_id in our data")
            try:
                image_to_associate = Image.objects.get(id=row.image_id)
            except:
                print(str(row.image_id) + " doesn't match a image_id in our data")

            # save it to the new database (using 'default')
            (obj, created_bool) = ImagePerson.objects.using('default').get_or_create(image=image_to_associate,
                                                                        person=person_to_associate, created_at = make_aware(row.created_at))
            print("making image_person row for image: " + str(row.image_id) + ", person: " + str(row.person_id))


    def populate_stories(self):
        ported_stories = Story.objects.using('source').all()
        for story_row in ported_stories:

            # save it to the new database (using 'default')
            (obj, created_bool) = Story.objects.using('default').get_or_create(id=story_row.id, description=story_row.description,
                                           image=story_row.image, intro=story_row.intro, slug=story_row.slug, source=story_row.source,
                                           created_at=make_aware(story_row.created_at), updated_at=make_aware(story_row.updated_at))
            print("adding story: " + str(story_row.description))

    def populate_person_story_rows(self):
        ported_data = PersonStory.objects.using('source').all()

        for row in ported_data:
            try:
                person_to_associate = Person.objects.get(id=row.person_id)
            except:
                print(str(row.person_id) + " doesn't match a person_id in our data")
            try:
                story_to_associate = Story.objects.get(id=row.story_id)
            except:
                print(str(row.story_id) + " doesn't match a story_id in our data")

            # save it to the new database (using 'default')
            (obj, created_bool) = PersonStory.objects.using('default').get_or_create(story=story_to_associate,
                                                person=person_to_associate, created_at = make_aware(row.created_at))
            print("making person_story row for story: " + str(row.story_id) + ", person: " + str(row.person_id))

    def populate_logins(self):
        with connections['source'].cursor() as cursor:
            cursor.execute('select * from logins')
            data = cursor.fetchall()

        for row in data:
            print(row)
            row_list = list(row)
            try:
                user_to_associate = User.objects.get(id=row_list[1])
            except:
                print(str(row_list[1]) + " doesn't match a user_id in our data")
            else:
                (obj, created_bool) = Login.objects.using('default').get_or_create(
                                                        created_at=make_aware(row_list[2]), updated_at=make_aware(row_list[3]))
                obj.user.add(user_to_associate)
                obj.save()

    def populate_family_story_rows(self):
        ported_data = FamilyStory.objects.using('source').all()

        for row in ported_data:
            try:
                family_to_associate = Family.objects.get(id=row.family_id)
            except:
                print(str(row.family_id) + " doesn't match a family_id in our data")
            try:
                story_to_associate = Story.objects.get(id=row.story_id)
            except:
                print(str(row.story_id) + " doesn't match a story_id in our data")

            # save it to the new database (using 'default')
            (obj, created_bool) = FamilyStory.objects.using('default').get_or_create(story=story_to_associate,
                                                family=family_to_associate, created_at = make_aware(row.created_at))
            print("making family_story row for story: " + str(row.story_id) + ", family: " + str(row.family_id))


    def populate_person_video_rows(self):
        ported_data = VideoPerson.objects.using('source').all()

        for row in ported_data:
            description = row.description
            try:
                person_to_associate = Person.objects.get(id=row.person_id)
            except:
                print(str(row.person_id) + " doesn't match a person_id in our data")
            try:
                video_to_associate = Video.objects.get(id=row.video_id)
            except:
                print(str(row.video_id) + " doesn't match a video_id in our data")

            # save it to the new database (using 'default')
            (obj, created_bool) = VideoPerson.objects.using('default').get_or_create(video=video_to_associate,
                                    person=person_to_associate, description = description, created_at = make_aware(row.created_at))
            print("making video_person row for video: " + str(row.video_id) + ", person: " + str(row.person_id))


    def handle(self, *args, **kwargs):
        print("CALLING populate_image_person_rows")
        self.populate_image_person_rows()
        print("CALLING populate_stories")
        self.populate_stories()
        print("CALLING populate_person_story_rows")
        self.populate_person_story_rows()
        print("CALLING populate_logins")
        self.populate_logins()
        print("CALLING populate_family_story_rows")
        self.populate_family_story_rows()
        print("CALLING populate_person_video_rows")
        self.populate_person_video_rows()
