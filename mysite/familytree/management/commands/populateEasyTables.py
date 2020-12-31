from django.core.management.base import BaseCommand, CommandError
from ...models import Person, Image, ImagePerson, Note, Family, Story, PersonStory
from pathlib import Path
import csv

class Command(BaseCommand):
    help = 'Migrates notes and image_person data from previous database(internal use)'

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
                                                                        person=person_to_associate, created_at = row.created_at)
            print("making image_person row for image: " + str(row.image_id) + ", person: " + str(row.person_id))


    def populate_stories(self):
        ported_stories = Story.objects.using('source').all()
        for story_row in ported_stories:

            # save it to the new database (using 'default')
            (obj, created_bool) = Story.objects.using('default').get_or_create(id=story_row.id, description=story_row.description,
                                           image=story_row.image, intro=story_row.intro, slug=story_row.slug, source=story_row.source,
                                           created_at=story_row.created_at, updated_at=story_row.updated_at)
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
                                                person=person_to_associate, created_at = row.created_at)
            print("making person_story row for story: " + str(row.story_id) + ", person: " + str(row.person_id))

    def populate_notes(self):
        ported_notes = Note.objects.using('source').all()

        for note_row in ported_notes:

            print(note_row.body)
            # # In the old system, type 1 was for person
            #
            # # try:
            # #     author = Person.objects.get(id=note_row.author)
            # # except:
            # #     print(str(note_row.author) + " author doesn't match a person_id in our data")
            #
            # if note_row.type == 1:
            #     print("person note: ")
            #
            #     try:
            #         person_to_associate = Person.objects.get(id=note_row.ref_id)
            #     except:
            #         print(str(note_row.ref_id) + " doesn't match a person_id in our data")
            #
            #     # save it to the new database (using 'default')
            #     # (obj, created_bool) = Note.objects.using('default').get_or_create(image=image_to_associate,
            #     #                                                                              person=person_to_associate,
            #     #                                                                              created_at=row.created_at)
            #     #     print("making image_person row for image: " + str(row.image_id) + ", person: " + str(row.person_id))
            #
            #
            # # In the old system, type 2 was for family
            # if note_row.type == 2:
            #     print("family note: ")
            #     try:
            #         family_to_associate = Family.objects.get(id=note_row.ref_id)
            #     except:
            #         print(str(note_row.ref_id) + " doesn't match a family_id in our data")


    # author -> author_id
    # new fields: person_id, family_id


    # type = models.IntegerField(null=True)  # 1 for person, 2 for family
    # author = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='author')
    # author_name = models.CharField(max_length=50, blank=True)
    # body = models.CharField(max_length=1000, blank=True)
    # date = models.DateField(null=True, blank=True)
    # person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='note_person')
    # family = models.ForeignKey(Family, null=True, blank=True, on_delete=models.SET_NULL, related_name='family_note')
    # active = models.BooleanField(null=True, default=True)
    # for_self = models.BooleanField(null=True, default=False)
    # created_at = models.DateTimeField(null=True, blank=True)
    # updated_at = models.DateTimeField(null=True, blank=True)






    def handle(self, *args, **kwargs):

        #self.populate_image_person_rows()
        # self.populate_notes()
        #self.populate_stories()
        self.populate_person_story_rows()

