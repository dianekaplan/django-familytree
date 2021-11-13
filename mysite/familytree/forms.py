from django.forms import ModelForm

from .models import Note, Person


class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ["author_name", "body", "author", "person", "family"]


class EditPersonForm(ModelForm):
    class Meta:
        model = Person
        fields = [
            "first",
            "nickname",
            "last",
            "maiden",
            "middle",
            "birthdate",
            "birthdate_note",
            "birthplace",
            "education",
            "work",
            "interests",
            "current_location",
            "notes1",
            "notes2",
            "notes3",
            "deathdate",
            "deathdate_note",
        ]
