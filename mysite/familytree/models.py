from datetime import timezone, datetime

from django.db import models


class Person(models.Model):
    gedcom_indi = models.CharField(max_length=10, blank=True, default='')
    gedcom_UUID = models.CharField(max_length=40, blank=True, default='')
    first = models.CharField(max_length=30, blank=True, default='')
    middle = models.CharField(max_length=20, blank=True, default='')
    last = models.CharField(max_length=20, blank=True, default='')
    maiden = models.CharField(max_length=20, blank=True, default='')
    nickname = models.CharField(max_length=20, blank=True, default='')
    display_name = models.CharField(max_length=40)
    birthdate = models.DateField(null=True, blank=True)
    birthdate_note = models.CharField(max_length=55, blank=True, default='')
    birthplace = models.CharField(max_length=60, blank=True, default='')
    origin_family = models.ForeignKey('Family', null=True, blank=True, on_delete=models.SET_NULL)
    orig_fam_indi = models.CharField(max_length=10, blank=True, default='')
    keem_line = models.BooleanField(null=True, default=False)
    husband_line = models.BooleanField(null=True, default=False)
    kemler_line = models.BooleanField(null=True, default=False)
    kaplan_line = models.BooleanField(null=True, default=False)
    sex = models.CharField(max_length=2, blank=True, default='')
    origin = models.CharField(max_length=100, blank=True, default='') # big description of background, probably will remove
    face = models.CharField(max_length=20, blank=True, default='')
    current_location = models.CharField(max_length=20, blank=True, default='')
    work = models.CharField(max_length=150, blank=True, default='')
    interests = models.CharField(max_length=150, blank=True, default='')
    education = models.CharField(max_length=150, blank=True, default='')
    resting_place = models.CharField(max_length=60, blank=True, default='')
    deathdate_note = models.CharField(max_length=40, blank=True, default='')
    hidden = models.BooleanField(null=True, default=False)
    adopted = models.BooleanField(null=True, default=False)
    direct_line = models.BooleanField(null=True, default=False)
    show_on_landing_page = models.BooleanField(null=False, default=False)
    sibling_seq = models.IntegerField(blank=True, null=True)  # will later update families to handle this individually
    notes1 = models.CharField(max_length=150, blank=True, default='')
    notes2 = models.CharField(max_length=150, blank=True, default='')
    notes3 = models.CharField(max_length=150, blank=True, default='')
    flag1 = models.CharField(max_length=10, blank=True, default='') # will probably get rid of these anyway
    flag2 = models.CharField(max_length=10, blank=True, default='') # will probably get rid of these anyway
    flag3 = models.CharField(max_length=10, blank=True, default='') # will probably get rid of these anyway
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    reviewed = models.BooleanField(null=True, default=False)
    # group_images = models.ManyToManyField(models.Image)

    class Meta(object):
        verbose_name_plural = 'People'
        db_table = 'people'

    def unreviewed_person(self):
        return self.reviewed == False

    def __str__(self):
        return self.first + " " + self.last


class Family(models.Model):
    gedcom_indi = models.CharField(max_length=10, blank=True, default='')
    display_name = models.CharField(max_length=50, blank=True)
    wife = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='partner1')
    husband = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='partner2')
    wife_indi = models.CharField(max_length=10, blank=True, default='')
    husband_indi = models.CharField(max_length=10, blank=True, default='')
    child_indi = models.CharField(max_length=10, blank=True, default='')  # temporary- still need this?
    no_kids_bool = models.BooleanField(null=True)
    keem_line = models.BooleanField(null=True, default=False)
    husband_line = models.BooleanField(null=True, default=False)
    kemler_line = models.BooleanField(null=True, default=False)
    kaplan_line = models.BooleanField(null=True, default=False)
    marriage_date = models.DateField(null=True, blank=True)
    marriage_date_note = models.CharField(max_length=30, blank=True, default='')
    divorced = models.BooleanField(null=True, default=False)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    show_on_branch_view = models.BooleanField(null=False, default=False)
    sequence = models.IntegerField(blank=True, null=True)
    branch = models.IntegerField(blank=True, null=True)
    branch_seq = models.IntegerField(blank=True, null=True)
    flag1 = models.CharField(max_length=10, blank=True, default='') # will probably get rid of these anyway
    flag2 = models.CharField(max_length=10, blank=True, default='') # will probably get rid of these anyway
    reviewed = models.BooleanField(null=True, default=False)

    class Meta(object):
        verbose_name_plural = 'Families'
        db_table = 'families'

    def unreviewed_family(self):
        return self.reviewed == False

    def __str__(self):
        return self.display_name

class Image(models.Model):
    big_name = models.CharField(max_length=50, blank=True) # this field will always be there
    med_name = models.CharField(max_length=50, blank=True) # optional file name for different medium sized image (rather than just resized)
    little_name = models.CharField(max_length=50, blank=True) # optional file name for zoomed-in thumbnail (rather than just resized)
    caption = models.CharField(max_length=50, blank=True)
    year = models.CharField(max_length=10, blank=True)
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='person')
    family = models.ForeignKey(Family, null=True, blank=True, on_delete=models.SET_NULL, related_name='family')
    featured = models.IntegerField(null=True, default=False)
    keem_line = models.BooleanField(null=True, default=False)
    husband_line = models.BooleanField(null=True, default=False)
    kemler_line = models.BooleanField(null=True, default=False)
    kaplan_line = models.BooleanField(null=True, default=False)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta(object):
        verbose_name_plural = 'Images'
        db_table = 'images'

    def __str__(self):
        return self.big_name

class ImagePerson(models.Model):
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name='image_id')
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='person_id')
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta(object):
        verbose_name_plural = 'ImagePerson records'
        db_table = 'image_person'

    def __str__(self):
        return str(self.image_id)

class Note(models.Model):
    type = models.IntegerField(null=True)  # 1 for person, 2 for family
    author = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='author')
    author_name = models.CharField(max_length=50, blank=True)
    body = models.CharField(max_length=1000, blank=True)
    date = models.DateField(null=True, blank=True)
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='note_person')
    family = models.ForeignKey(Family, null=True, blank=True, on_delete=models.SET_NULL, related_name='family_note')
    active = models.BooleanField(null=True, default=True)
    for_self = models.BooleanField(null=True, default=False)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta(object):
        verbose_name_plural = 'Notes'
        db_table = 'notes'

    def __str__(self):
        return self.author_name + self.body