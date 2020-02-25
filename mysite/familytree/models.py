from django.db import models


class Person(models.Model):
    first_name = models.CharField(max_length=30, blank=True, default='')
    last_name = models.CharField(max_length=30, blank=True, default='')
    display_name = models.CharField(max_length=40)
    dob = models.DateField(null=True)
    dob_string = models.CharField(max_length=30, blank=True, default='')
    dob_place = models.CharField(max_length=30, blank=True, default='')
    origin_family= models.ForeignKey('Family', null=True, blank=True, on_delete=models.SET_NULL)
    sex = models.CharField(max_length=2, blank=True, default='')
    occupation = models.CharField(max_length=75, blank=True, default='')
    death_place = models.CharField(max_length=30, blank=True, default='')
    death_date_note = models.CharField(max_length=30, blank=True, default='')

    def __str__(self):
        return self.display_name


class Family(models.Model):
    display_name = models.CharField(max_length=50)
    partner1 = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='partner1')
    partner2 = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='partner2')
    no_kids = bool
    marriage_date = models.DateField(null=True)
    marriage_date_string = models.CharField(max_length=30, blank=True, default='')

    def __str__(self):
        return self.display_name
