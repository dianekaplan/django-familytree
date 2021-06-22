from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.db import models
from django.forms import TextInput, Textarea
# from base import Login

# import sys
# import os
# print("sys.path has: " + str(sys.path))
# print("os.getcwd() gives: " + str(os.getcwd()))

# from mysite.myauth.models import Login  # No module named 'mysite.myauth'
# from ..myauth import Login

from .models import Person, Family, Image, ImagePerson, Note, Branch, Profile, Story, PersonStory, Video, Audiofile, \
    VideoPerson, FamilyStory

admin.site.register(LogEntry)
# class LogAdmin(admin.ModelAdmin):
#     list_display = ('action_time','user','content_type','change_message','is_addition','is_change','is_deletion')
#     list_filter = ['action_time','user','content_type']
#     ordering = ('-action_time',)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ('display_name', 'first', 'last')
    list_display = ('display_name', 'birthdate', 'birthyear', 'birthdate_note', 'gedcom_uuid', 'family_id', 'direct_line', 'living',
                    'show_on_landing_page', 'created_at', 'reviewed')
    ordering = ('-created_at', 'display_name')
    raw_id_fields = ('family',)
    pass


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    search_fields = ('display_name',)
    list_display = ('display_name', 'direct_family_number','show_on_branch_view', 'branch_seq', 'created_at', 'reviewed')
    raw_id_fields = ('wife','husband',)
    ordering = ('-created_at', 'display_name')
    pass


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    search_fields = ('big_name',)
    list_display = ('big_name', 'year','created_at')
    ordering = ('-created_at', 'big_name')
    raw_id_fields = ('person','family')
    pass


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    search_fields = ('description',)
    list_display = ('description', 'image', 'intro', 'slug', 'source','created_at')
    ordering = ('-created_at', 'description')
    pass


@admin.register(PersonStory)
class PersonStoryAdmin(admin.ModelAdmin):
    search_fields = ('story_id',)
    list_display = ('story_id', 'person_id', 'created_at')
    ordering = ('-created_at', 'story_id')
    raw_id_fields = ('person',)
    pass


@admin.register(FamilyStory)
class FamilyStoryAdmin(admin.ModelAdmin):
    search_fields = ('story_id',)
    list_display = ('story_id', 'family_id', 'created_at')
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
    raw_id_fields = ('author','person','family')
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

# class LoginInline(admin.StackedInline):
#     model = Login

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # search_fields = ('user',)
    list_display = ('user', 'person', 'connection_notes')
    # inlines = [LoginInline]
    pass


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'caption', 'year', 'created_at')
    ordering = ('-created_at', 'name')
    raw_id_fields = ('person',)
    pass


@admin.register(VideoPerson)
class VideoPersonAdmin(admin.ModelAdmin):
    search_fields = ('video_id',)
    list_display = ('video_id', 'person_id', 'description', 'created_at')
    ordering = ('-created_at', 'video_id')
    raw_id_fields = ('person',)
    pass


@admin.register(ImagePerson)
class ImagePersonAdmin(admin.ModelAdmin):
    search_fields = ('image_id',)
    list_display = ('image_id', 'person_id')
    ordering = ('-created_at', 'image_id')
    raw_id_fields = ('person','image')
    pass


@admin.register(Audiofile)
class AudioAdmin(admin.ModelAdmin):
    search_fields = ('filename',)
    list_display = ('filename', 'recording_date', 'summary')
    ordering = ('-created_at', 'filename')
    raw_id_fields = ('person',)
    pass
