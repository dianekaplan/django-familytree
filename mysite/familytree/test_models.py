import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.mysite.settings")

# from django.contrib.auth.models import User
from django.test import TestCase

from .models import Branch, Family, Image, Person


def create_person(display_name):
    """
    Create a person with the given display name
    """
    return Person.objects.create(display_name=display_name)


def create_family(display_name, wife, husband):
    """
    Create a family with the given display name
    """
    return Family.objects.create(display_name=display_name, wife=wife, husband=husband)


def create_image(big_name):
    """
    Create an image with the given name
    """
    return Image.objects.create(big_name=big_name)


def create_branch(display_name):
    """
    Create a branch with the given name
    """
    return Branch.objects.create(display_name=display_name)


#
# def create_profile(user):
#     """
#     Create a profile for the given user
#     """
#     return Profile.objects.create(user=user)


class PersonModelTests(TestCase):
    def setUp(self):
        self.person = Person()
        self.person.display_name = "Marcia Brady"
        self.person.sex = "F"
        self.person.save()

    def test_fields(self):
        person = Person()
        person.display_name = "Jan Brady"
        person.sex = "F"
        person.save()

        record = Person.objects.get(pk=person.id)
        self.assertEqual(record, person)

    def test_default_stories(self):
        """
        default person returns None for stories
        """
        self.assertIsNone(self.person.has_stories())

    def test_default_families(self):
        """
        default person has no families made
        """
        self.assertEqual(len(self.person.families_made()), 0)

    def test_default_group_images(self):
        """
        default person has no group images
        """
        self.assertEqual(len(self.person.group_images()), 0)

    def test_unreviewed_person(self):
        """
        unreviewed_person() returns True when reviewed flag is False (default), otherwise False
        """

        self.assertIs(self.person.unreviewed_person(), True)

        # update reviewed = True, and make sure unreviewed_person() now returns false
        self.person.reviewed = True
        self.assertIs(self.person.unreviewed_person(), False)


class FamilyModelTests(TestCase):
    def test_unreviewed_family(self):
        """
        unreviewed_family() returns True for family whose reviewed flag is False
        """
        unreviewed_family = Family(reviewed=False)
        self.assertIs(unreviewed_family.unreviewed_family(), True)
