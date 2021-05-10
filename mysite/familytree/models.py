from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


class Branch(models.Model):
    display_name = models.CharField(max_length=50, blank=True)

    class Meta(object):
        verbose_name_plural = 'Branches'
        db_table = 'branches'

    def __str__(self):
        return self.display_name


class Person(models.Model):
    gedcom_indi = models.CharField(max_length=10, null=True, blank=True, default='')
    gedcom_uuid = models.CharField(max_length=200, null=True, blank=True, default='')
    first = models.CharField(max_length=30, blank=True, default='')
    middle = models.CharField(max_length=20, null=True, blank=True, default='')
    last = models.CharField(max_length=20, blank=True, default='')
    maiden = models.CharField(max_length=20, null=True, blank=True, default='')
    nickname = models.CharField(max_length=20, null=True, blank=True, default='')
    display_name = models.CharField(max_length=40, null=True)
    branches = models.ManyToManyField(Branch, blank=True)

    birthdate = models.DateField(null=True, blank=True)
    birthdate_note = models.CharField(max_length=55, null=True, blank=True, default='')
    birthyear = models.IntegerField(blank=True, null=True)
    birthplace = models.CharField(max_length=60, null=True, blank=True, default='')
    family = models.ForeignKey('Family', null=True, blank=True, on_delete=models.SET_NULL) # person's origin family
    orig_fam_indi = models.CharField(max_length=10, null=True, blank=True, default='')
    sex = models.CharField(max_length=2, null=True, blank=True, default='')
    origin = models.CharField(max_length=100, null=True, blank=True, default='') # big description of background, probably will remove
    face = models.CharField(max_length=25, null=True, blank=True, default='')
    current_location = models.CharField(max_length=75, null=True, blank=True, default='')
    work = models.CharField(max_length=300, null=True, blank=True, default='')
    interests = models.CharField(max_length=300, null=True, blank=True, default='')
    education = models.CharField(max_length=300, null=True, blank=True, default='')
    death_place = models.CharField(max_length=100, null=True, blank=True, default='')
    deathdate = models.DateField(null=True, blank=True)
    deathdate_note = models.CharField(max_length=175, null=True, blank=True, default='')
    hidden = models.BooleanField(null=True, default=False)
    adopted = models.BooleanField(null=True, default=False)
    direct_line = models.BooleanField(null=True, default=False)
    show_on_landing_page = models.BooleanField(null=True, default=False)
    sibling_seq = models.IntegerField(blank=True, null=True)  # will later update families to handle this individually
    notes1 = models.CharField(max_length=600, null=True, blank=True, default='')
    notes2 = models.CharField(max_length=600, null=True, blank=True, default='')
    notes3 = models.CharField(max_length=600, null=True, blank=True, default='')
    flag1 = models.CharField(max_length=10, null=True, blank=True, default='') # will probably get rid of these anyway
    flag2 = models.CharField(max_length=10, null=True, blank=True, default='') # will probably get rid of these anyway
    flag3 = models.CharField(max_length=10, null=True, blank=True, default='') # will probably get rid of these anyway
    reviewed = models.BooleanField(null=True, default=False)
    living = models.BooleanField(null=True, default=False)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    def has_stories(self):
        try:
            person_story_records = PersonStory.objects.filter(person_id=self.id)
        except PersonStory.DoesNotExist:
            person_story_records = None
        if person_story_records:
            return True

    class Meta(object):
        verbose_name_plural = 'People'
        db_table = 'people'

    def unreviewed_person(self):
        return self.reviewed == False

    def __str__(self):
        return self.first + " " + self.last


class Family(models.Model):
    gedcom_indi = models.CharField(max_length=10, null=True, blank=True, default='')
    display_name = models.CharField(max_length=50, blank=True)
    wife = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='partner1')
    husband = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='partner2')
    wife_indi = models.CharField(max_length=10, null=True, blank=True, default='')
    husband_indi = models.CharField(max_length=10, null=True, blank=True, default='')
    child_indi = models.CharField(max_length=10, null=True, blank=True, default='')  # temporary- still need this?
    no_kids_bool = models.BooleanField(null=True)
    original_family = models.BooleanField(null=True)
    original_family_text = models.CharField(max_length=600, null=True, blank=True, default='')
    branches = models.ManyToManyField(Branch, blank=True)
    direct_family_number = models.IntegerField(blank=True, null=True)
    marriage_date = models.DateField(null=True, blank=True)
    marriage_date_note = models.CharField(max_length=100, null=True, blank=True, default='')
    divorced = models.BooleanField(null=True, default=False)
    show_on_branch_view = models.BooleanField(null=True, default=False)
    sequence = models.IntegerField(blank=True, null=True)
    notes1 = models.CharField(max_length=600, null=True, blank=True, default='')
    notes2 = models.CharField(max_length=600, null=True, blank=True, default='')
    branch_seq = models.IntegerField(blank=True, null=True)
    reviewed = models.BooleanField(null=True, default=False)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta(object):
        verbose_name_plural = 'Families'
        db_table = 'families'

    def unreviewed_family(self):
        return self.reviewed == False

    def __str__(self):
        return self.display_name


class Image(models.Model):
    big_name = models.CharField(max_length=50, null=True, blank=True) # this field will always be there
    med_name = models.CharField(max_length=50, null=True, blank=True) # optional file name for different medium sized image (rather than just resized)
    little_name = models.CharField(max_length=50, null=True, blank=True) # optional file name for zoomed-in thumbnail (rather than just resized)
    caption = models.CharField(max_length=50, null=True, blank=True)
    branches = models.ManyToManyField(Branch, blank=True)

    year = models.CharField(max_length=20, null=True, blank=True)
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='person')
    family = models.ForeignKey(Family, null=True, blank=True, on_delete=models.SET_NULL, related_name='family')
    featured = models.IntegerField(null=True, default=False)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    def image_subjects(self):
        image_people = set()

        # get the featured person, if there is one
        if self.person:
            this_image_person = Person.objects.get(id=self.person_id)
        else:
            this_image_person = None

        # get the featured family, if there is one
        if self.family:
            this_image_family = Family.objects.get(id=self.family_id)
            if this_image_family.wife:
                image_people.add(this_image_family.wife)
            if this_image_family.husband:
                image_people.add(this_image_family.husband)
            kids = Person.objects.filter(family=self.family)
            if kids:
                for kid in kids:
                    image_people.add(kid)
        else:
            this_image_family = None

        # Get the queryset for ImagePerson records, then get the people from that
        image_person_records = ImagePerson.objects.filter(image_id=self.id)
        for record in image_person_records:
            person = Person.objects.get(id = record.person_id)
            image_people.add(person)

        return this_image_person, this_image_family, image_people

    class Meta(object):
        verbose_name_plural = 'Images'
        db_table = 'images'

    def __str__(self):
        return self.big_name


class ImagePerson(models.Model):
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name='image_id')
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='person_id')
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    class Meta(object):
        verbose_name_plural = 'ImagePerson records'
        db_table = 'image_person'

    def __str__(self):
        return str(self.image_id)


class Profile(models.Model): # This class holds additional info for user records
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    person = models.ForeignKey('Person', null=True, blank=True, on_delete=models.SET_NULL)
    branches = models.ManyToManyField(Branch, blank=True)
    logins = models.IntegerField(null=True, default=0)
    last_login = models.DateField(null=True, blank=True)
    last_pestered = models.DateField(null=True, blank=True)
    connection_notes = models.CharField(null=True, max_length=250, blank=True)
    furthest_html = models.CharField(null=True, max_length=250, blank=True)
    shared_account = models.BooleanField(null=True, default=False)

    class Meta(object):
        verbose_name_plural = 'Profiles'
        db_table = 'profiles'

    def __str__(self):
        return self.person.display_name


class Story(models.Model):
    description = models.CharField(max_length=255, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True) # note- this is NOT an Image object
    intro = models.CharField(max_length=2000, null=True, blank=True)
    slug = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta(object):
        verbose_name_plural = 'Stories'
        db_table = 'stories'

    def __str__(self):
        return self.description


class PersonStory(models.Model):
    story = models.ForeignKey(Story, null=True, blank=True, on_delete=models.SET_NULL)
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta(object):
        verbose_name_plural = 'PersonStory records'
        db_table = 'person_story'

    def __str__(self):
        return str(self.story.description)


class FamilyStory(models.Model):
    story = models.ForeignKey(Story, null=True, blank=True, on_delete=models.SET_NULL)
    family = models.ForeignKey(Family, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta(object):
        verbose_name_plural = 'FamilyStory records'
        db_table = 'family_story'

    def __str__(self):
        return str(self.story.description)


# class Login(models.Model):
#     user = models.ManyToManyField(User)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         #managed = False
#         db_table = 'logins'
#
#     def __str__(self):
#         return str(self.created_at)


class Video(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    caption = models.CharField(max_length=255, blank=True, null=True)
    year = models.CharField(max_length=25, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    branches = models.ManyToManyField(Branch, blank=True)
    person = models.ManyToManyField(Person, blank=True)
    family = models.ManyToManyField(Family, blank=True)

    def video_subjects(self):
        # Get the queryset for VideoPerson records, then get the people from that
        video_person_records = VideoPerson.objects.filter(video_id=self.id)
        video_people = set()
        for record in video_person_records:
            person = Person.objects.filter(id = record.person_id)
            video_people.add(person)
        return video_people

    class Meta:
        #managed = False
        db_table = 'videos'

    def __str__(self):
        return self.name


class VideoPerson(models.Model):
    video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL, related_name='video_id')
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='vid_person_id')
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta(object):
        verbose_name_plural = 'VideoPerson records'
        db_table = 'person_video'

    def __str__(self):
        return str(self.video_id)

class Note(models.Model):
    author = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='author')
    author_name = models.CharField(max_length=50, null=True, blank=True)
    body = models.CharField(max_length=3000, blank=True)
    date = models.DateField(null=True, blank=True)
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='note_person')
    family = models.ForeignKey(Family, null=True, blank=True, on_delete=models.SET_NULL, related_name='family_note')
    active = models.BooleanField(null=True, default=True)
    for_self = models.BooleanField(null=True, default=False)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta(object):
        verbose_name_plural = 'Notes'
        db_table = 'notes'

    def __str__(self):
        return self.author_name + self.body


class Audiofile(models.Model):
    filename = models.CharField(max_length=150, blank=True, null=True)
    summary = models.CharField(max_length=255, blank=True, null=True)
    recording_date = models.DateField(blank=True, null=True)
    person = models.ManyToManyField(Person, blank=True)
    branches = models.ManyToManyField(Branch, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        #managed = False
        db_table = 'audiofiles'
