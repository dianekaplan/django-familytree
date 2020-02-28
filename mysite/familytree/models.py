from django.db import models


class Person(models.Model):
    gedcom_indi = models.CharField(max_length=30, blank=True, default='')
    gedcom_UUID = models.CharField(max_length=30, blank=True, default='')
    first_name = models.CharField(max_length=30, blank=True, default='')
    last_name = models.CharField(max_length=30, blank=True, default='')
    display_name = models.CharField(max_length=40)
    dob = models.DateField(null=True, blank=True)
    dob_string = models.CharField(max_length=30, blank=True, default='')
    dob_place = models.CharField(max_length=30, blank=True, default='')
    origin_family = models.ForeignKey('Family', null=True, blank=True, on_delete=models.SET_NULL)
    orig_fam_indi = models.CharField(max_length=30, blank=True, default='')
    sex = models.CharField(max_length=2, blank=True, default='')
    occupation = models.CharField(max_length=75, blank=True, default='')
    death_place = models.CharField(max_length=30, blank=True, default='')
    death_date_note = models.CharField(max_length=30, blank=True, default='')
    hidden = models.BooleanField(null=False, default=False)

    class Meta(object):
        verbose_name_plural = 'People'

    def __str__(self):
        return self.display_name


class Family(models.Model):
    gedcom_indi = models.CharField(max_length=10, blank=True, default='')
    display_name = models.CharField(max_length=50)
    wife = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='partner1')
    husband = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='partner2')
    wife_indi = models.CharField(max_length=10, blank=True, default='')
    husband_indi = models.CharField(max_length=10, blank=True, default='')
    child_indi = models.CharField(max_length=10, blank=True, default='')
    no_kids = models.BooleanField(null=True)
    marriage_date = models.DateField(null=True)
    marriage_date_string = models.CharField(max_length=30, blank=True, default='')

    class Meta(object):
        verbose_name_plural = 'Families'

    def __str__(self):
        return self.display_name
