from django.contrib import admin

from .models import Person, Family

#admin.site.register(Person)
#admin.site.register(Family)

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ('display_name', 'first', 'last')
    list_display = ('display_name', 'birthdate_note', 'origin_family', 'gedcom_UUID', 'keem_line', 'husband_line', 'kemler_line', 'kaplan_line','created_at', 'reviewed')
    ordering = ('-created_at', 'display_name')
    pass

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    search_fields = ('display_name',)
    list_display = ('display_name', 'keem_line', 'husband_line', 'kemler_line', 'kaplan_line','created_at', 'reviewed')
    ordering = ('-created_at', 'display_name')
    pass