from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea

from .models import Person, Family, Image, ImagePerson, Note, Branch, Profile, Story, PersonStory


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ('display_name', 'first', 'last')
    list_display = ('display_name', 'birthdate_note', 'family_id', 'gedcom_uuid', 'keem_line', 'husband_line', 'kemler_line', 'kaplan_line','created_at', 'reviewed')
    ordering = ('-created_at', 'display_name')
    pass

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    search_fields = ('display_name',)
    list_display = ('display_name', 'keem_line', 'husband_line', 'kemler_line', 'kaplan_line','created_at', 'reviewed')
    ordering = ('-created_at', 'display_name')
    pass

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    search_fields = ('big_name',)
    list_display = ('big_name', 'year', 'keem_line', 'husband_line', 'kemler_line', 'kaplan_line','created_at')
    ordering = ('-created_at', 'big_name')
    pass

@admin.register(ImagePerson)
class ImagePersonAdmin(admin.ModelAdmin):
    search_fields = ('person_id',)
    list_display = ('image_id', 'person_id', 'created_at')
    ordering = ('-created_at', 'image_id')
    pass

@admin.register(Story)
class ImageAdmin(admin.ModelAdmin):
    search_fields = ('description',)
    list_display = ('description', 'image', 'intro', 'slug', 'source','created_at')
    ordering = ('-created_at', 'description')
    pass

@admin.register(PersonStory)
class PersonStoryAdmin(admin.ModelAdmin):
    search_fields = ('story_id',)
    list_display = ('story_id', 'person_id', 'created_at')
    ordering = ('-created_at', 'story_id')
    pass


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    search_fields = ('author_name',)
    list_display = ('author_name', 'person_id', 'family_id','created_at')
    ordering = ('-created_at', 'author_name')

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'200', 'rows':2})},
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }
    pass

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    search_fields = ('display_name',)
    list_display = ('id', 'display_name')

    # formfield_overrides = {
    #     models.CharField: {'widget': TextInput(attrs={'size':'200', 'rows':2})},
    #     models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    # }
    pass

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'person', 'connection_notes')
    pass
