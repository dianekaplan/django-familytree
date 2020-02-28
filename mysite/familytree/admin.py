from django.contrib import admin

from .models import Person, Family

#admin.site.register(Person)
#admin.site.register(Family)

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ('display_name',)
    pass

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    search_fields = ('display_name',)
    pass