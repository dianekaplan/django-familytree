from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.utils.safestring import mark_safe

DJANGO_SITE_CREATION = settings.DJANGO_SITE_CREATION

class Branch(models.Model):
    display_name = models.CharField(max_length=50, blank=True)

    class Meta(object):
        verbose_name_plural = 'Branches'
        db_table = 'branches'

    def __str__(self):
        return self.display_name


class Person(models.Model):
    gedcom_indi = models.CharField(max_length=20, null=True, blank=True, default='')
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
    orig_fam_indi = models.CharField(max_length=20, null=True, blank=True, default='')
    sex = models.CharField(max_length=2, null=True, blank=True, default='')
    origin = models.CharField(max_length=100, null=True, blank=True, default='') # description of background
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
    notes1 = models.CharField(max_length=1200, null=True, blank=True, default='')
    notes2 = models.CharField(max_length=1200, null=True, blank=True, default='')
    notes3 = models.CharField(max_length=1200, null=True, blank=True, default='')
    flag1 = models.CharField(max_length=10, null=True, blank=True, default='') # not using anymore
    flag2 = models.CharField(max_length=10, null=True, blank=True, default='') # not using anymore
    flag3 = models.CharField(max_length=10, null=True, blank=True, default='') # not using anymore
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

    def families_made(self):
        try:
            wife_of = Family.objects.filter(wife=self.id)
            husband_of = Family.objects.filter(husband=self.id)
            families_made = wife_of | husband_of
        except Family.DoesNotExist:
            families_made = None
        return families_made

    def group_images(self):
        group_images = Image.objects.none()

        # add the ones from image_person
        group_image_listings = ImagePerson.objects.filter(person_id=self.id).order_by('image__year')
        for listing in group_image_listings:
            this_image = Image.objects.filter(id=listing.image_id)
            group_images = group_images | this_image

        # add the ones for original family, if the image year >= person's birth year
        if self.family:
            family_images = Image.objects.filter(family=self.family).filter(spouses_only=False)

            for image in family_images:
                if self.birthyear and image.year_as_int() >= self.birthyear:
                    group_images = group_images | Image.objects.filter(id=image.id)

        # add the ones for families made
        families_made = self.families_made()
        if families_made:
            for family in families_made:
                group_images = group_images | Image.objects.filter(family=family)

        return group_images.order_by('year').distinct()

    class Meta(object):
        verbose_name_plural = 'People'
        db_table = 'people'

    def unreviewed_person(self):
        return self.reviewed == False

    def __str__(self):
        return self.first + " " + self.last


class Family(models.Model):
    gedcom_indi = models.CharField(max_length=20, null=True, blank=True, default='')
    display_name = models.CharField(max_length=60, blank=True)
    wife = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='partner1')
    husband = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='partner2')
    wife_indi = models.CharField(max_length=20, null=True, blank=True, default='')
    husband_indi = models.CharField(max_length=20, null=True, blank=True, default='')
    child_indi = models.CharField(max_length=20, null=True, blank=True, default='')  # temporary- still need this?
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
    big_name = models.CharField(max_length=50, null=True, blank=True) # this field will always be present
    med_name = models.CharField(max_length=50, null=True, blank=True) # optional file name for different medium sized image (rather than just resized)
    little_name = models.CharField(max_length=50, null=True, blank=True) # optional file name for zoomed-in thumbnail (rather than just resized)
    caption = models.CharField(max_length=50, null=True, blank=True)
    notes = models.CharField(max_length=500, null=True, blank=True)
    branches = models.ManyToManyField(Branch, blank=True)

    year = models.CharField(max_length=20, null=True, blank=True)
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='person')
    family = models.ForeignKey(Family, null=True, blank=True, on_delete=models.SET_NULL, related_name='family')
    spouses_only = models.BooleanField(null=True, default=False)
    featured = models.IntegerField(null=True, default=False)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    def image_subjects(self):
        image_people = [] # use list instead of queryset to preserve display order on image detail page

        # get the featured person, if there is one
        if self.person:
            this_image_person = Person.objects.get(id=self.person_id)
        else:
            this_image_person = None

        # get the featured family, if there is one
        if self.family:
            this_image_family = Family.objects.get(id=self.family_id)
        else:
            this_image_family = None

        # Get the queryset for ImagePerson records, then get the people from that
        image_person_records = ImagePerson.objects.filter(image_id=self.id).order_by('id')
        for record in image_person_records:
            person = Person.objects.get(id=record.person_id)
            image_people.append(person)

        return this_image_person, this_image_family, image_people

    def pictured_list(self):
        this_image_person, this_image_family, image_people  = self.image_subjects()
        pictured_list = '<br/>'

        if this_image_person:
            pictured_list += this_image_person.display_name

        if image_people:  # if the image has both family and individuals configured, show people
            for person in image_people:
                pictured_list += person.display_name
                pictured_list += '<br/>'
        elif this_image_family:
            pictured_list += this_image_family.display_name

        pictured_list = mark_safe(pictured_list)

        return pictured_list

    def year_as_int(self):
        year_as_int = 0
        if len(self.year) == 4:
            year_as_int = int(self.year)
        return year_as_int

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
    login_count = models.IntegerField(null=True, default=0)
    last_pestered = models.DateField(null=True, blank=True)
    connection_notes = models.CharField(null=True, max_length=250, blank=True)
    furthest_html = models.CharField(null=True, max_length=250, blank=True)
    shared_account = models.BooleanField(null=True, default=False)
    guest_user = models.BooleanField(default=False)
    limited = models.BooleanField(default=True)
    timezone = models.CharField(null=True, max_length=100, default='US/Eastern')

    class Meta(object):
        verbose_name_plural = 'Profiles'
        db_table = 'profiles'

    def edits_made(self, type=None):
        if self.person:
            edits_made = LogEntry.objects.filter(user_id=self.user.id)
            if type == 'old':
                edits_made = [x for x in edits_made if x.action_time.date() < DJANGO_SITE_CREATION]
            if type == 'new':
                edits_made = [x for x in edits_made if x.action_time.date() >= DJANGO_SITE_CREATION]
            edit_counts = len(edits_made)
        else:
            edit_counts = False
        return edit_counts

    def old_edits_made(self):
        if self.person:
            edits_made_count = self.edits_made('old')
        else:
            edits_made_count = False
        return edits_made_count

    def new_edits_made(self):
        if self.person:
            edits_made_count = self.edits_made('new')
        else:
            edits_made_count = False
        return edits_made_count

    def notes_written(self, type):
        if self.person:
            all_notes = Note.objects.filter(author=self.person.id)
            if type == 'old':
                notes_written = [x for x in all_notes if x.created_at.date() < DJANGO_SITE_CREATION]
            elif type == 'new':
                notes_written = [x for x in all_notes if x.created_at.date() > DJANGO_SITE_CREATION]
            notes_written_count = len(notes_written) if notes_written else False
        else:
            notes_written_count = False
        return notes_written_count

    def old_notes_written(self):
        if self.person:
            notes_written_count = self.notes_written('old')
        else:
            notes_written_count = False
        return notes_written_count

    def new_notes_written(self):
        if self.person:
            notes_written_count = self.notes_written('new')
        else:
            notes_written_count = False
        return notes_written_count

    def last_login(self):
        return self.user.last_login

    # For a given profile, return an array of dates they logged in
    def get_logins(self):
        login_dates_queryset = list(Login.objects.filter(user_id=self.user.id).values('created_at'))
        login_dates = []
        for x in login_dates_queryset:
            login_dates.append(x.get('created_at').date())
        return login_dates

    def __str__(self):
        return self.user.username


class Story(models.Model):
    description = models.CharField(max_length=255, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True) # note- this is NOT an Image object
    intro = models.CharField(max_length=2000, null=True, blank=True)
    slug = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    branches = models.ManyToManyField(Branch, blank=True)
    dashboard_feature = models.BooleanField(null=True, default=True)

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
            person = Person.objects.filter(id = record.person_id).first()
            video_people.add(person)
        return video_people

    def pictured_list(self):
        video_subjects = self.video_subjects()
        pictured_list = ''

        if video_subjects:  # if the image has both family and individuals configured, show people
            for person in video_subjects:
                pictured_list += person.display_name
                pictured_list += '<br/>'
        pictured_list = mark_safe(pictured_list)

        return pictured_list

    class Meta:
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
    external_author = models.BooleanField(null=True, default=False)
    body = models.CharField(max_length=3000)
    date = models.DateField(null=True, blank=True, auto_now_add=True)
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
        return self.body


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


class Login(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'logins'


# signals
from django.core.mail import send_mail
from django.db.models.signals import post_save

from django.dispatch import receiver
from django.template.loader import render_to_string


@receiver(post_save, sender=User)
def send_login_email(sender, instance, **kwargs):

    email_data = {'user': instance}
    from_email = settings.ADMIN_EMAIL_SEND_FROM
    recipient_list = [settings.ADMIN_EMAIL_ADDRESS, ]
    subject = render_to_string(
        template_name='familytree/email/login_email_subject.txt'
    )
    html_message = render_to_string(
        'familytree/email/login_email_message.html', email_data
    )
    send_mail(subject, html_message, from_email, recipient_list, fail_silently=False, )
