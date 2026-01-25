from django.contrib import admin
from django.db import models
from django.forms import Textarea, TextInput

from .models import (
    Audiofile,
    Branch,
    Family,
    FamilyStory,
    Image,
    ImagePerson,
    Note,
    Person,
    PersonStory,
    Profile,
    Story,
    Video,
    VideoPerson,
)


@admin.action(description="Mark selected items as reviewed")
def make_reviewed(modeladmin, request, queryset):
    queryset.update(reviewed=True)


@admin.action(description="Mark selected items as shown on branch view")
def set_show_on_branch_view(modeladmin, request, queryset):
    queryset.update(show_on_branch_view=True)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ("display_name", "first", "last")
    list_display = (
        "display_name",
        "birthdate",
        "birthyear",
        "birthdate_note",
        "gedcom_uuid",
        "family_id",
        "direct_line",
        "living",
        "show_on_landing_page",
        "created_at",
        "reviewed",
    )
    ordering = ("-created_at", "display_name")
    raw_id_fields = ("family",)
    actions = [make_reviewed]
    pass


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    search_fields = ("display_name",)
    list_display = (
        "display_name",
        "direct_family_number",
        "show_on_branch_view",
        "branch_seq",
        "created_at",
        "reviewed",
    )
    raw_id_fields = ("wife", "husband")
    ordering = ("-created_at", "display_name")
    actions = [make_reviewed, set_show_on_branch_view]
    pass


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    search_fields = ("big_name",)
    list_display = ("big_name", "year", "created_at")
    ordering = ("-created_at", "big_name")
    raw_id_fields = ("person", "family")
    pass


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    search_fields = ("description",)
    list_display = ("description", "image", "intro", "slug", "source", "created_at")
    ordering = ("-created_at", "description")
    pass


@admin.register(PersonStory)
class PersonStoryAdmin(admin.ModelAdmin):
    search_fields = ("story_id",)
    list_display = ("story_id", "person_id", "created_at")
    ordering = ("-created_at", "story_id")
    raw_id_fields = ("person",)
    pass


@admin.register(FamilyStory)
class FamilyStoryAdmin(admin.ModelAdmin):
    search_fields = ("story_id",)
    list_display = ("story_id", "family_id", "created_at")
    ordering = ("-created_at", "story_id")
    raw_id_fields = ("family",)
    pass


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    search_fields = ("author_name",)
    list_display = ("author_name", "person_id", "family_id", "created_at")
    ordering = ("-created_at", "author_name")

    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "200", "rows": 2})},
        models.TextField: {"widget": Textarea(attrs={"rows": 4, "cols": 40})},
    }
    raw_id_fields = ("author", "person", "family")
    pass


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    search_fields = ("display_name",)
    list_display = ("id", "display_name")

    # formfield_overrides = {
    #     models.CharField: {'widget': TextInput(attrs={'size':'200', 'rows':2})},
    #     models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    # }
    pass


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "person", "login_count", "logins")
    ordering = ("login_count", "guest_user")

    raw_id_fields = ("person",)

    def logins(self, instance):
        return instance.get_logins()

    pass


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "caption", "year", "created_at")
    ordering = ("-created_at", "name")
    raw_id_fields = ("person",)
    pass


@admin.register(VideoPerson)
class VideoPersonAdmin(admin.ModelAdmin):
    search_fields = ("video_id",)
    list_display = ("video_id", "person_id", "description", "created_at")
    ordering = ("-created_at", "video_id")
    raw_id_fields = ("person",)
    pass


@admin.register(ImagePerson)
class ImagePersonAdmin(admin.ModelAdmin):
    search_fields = ("image__id",)
    list_display = ("image_id", "person_id")
    ordering = ("-created_at", "image_id")
    raw_id_fields = ("person", "image")
    pass


@admin.register(Audiofile)
class AudioAdmin(admin.ModelAdmin):
    search_fields = ("filename",)
    list_display = ("filename", "recording_date", "summary")
    ordering = ("-created_at", "filename")
    raw_id_fields = ("person",)
    pass
