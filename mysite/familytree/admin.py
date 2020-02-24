from django.contrib import admin

from .models import Person, Family

admin.site.register(Person)
admin.site.register(Family)