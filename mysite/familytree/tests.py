from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.urls import resolve, reverse

from .models import Branch, Family, Image, Person, Profile


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


class TestDetailViews(TestCase):
    def test_person_detail_view(self):
        """
        Test that person detail view loads
        """
        this_person = create_person(display_name="Marcia Brady")
        response = self.client.get(reverse("person_detail", args=(this_person.id,)))
        self.assertEqual(response.status_code, 302)

    def test_family_detail_view(self):
        """
        Test that family detail view loads
        """
        wife = create_person(display_name="Carol Brady")
        husband = create_person(display_name="Mike Brady")
        this_family = create_family(
            display_name="The Bradys (Mike & Carol)", wife=wife, husband=husband
        )
        response = self.client.get(reverse("family_detail", args=(this_family.id,)))
        self.assertEqual(response.status_code, 302)

    def test_image_detail_view(self):
        """
        Test that image detail view loads
        """
        this_image = create_image(big_name="blah.jpg")
        response = self.client.get(reverse("image_detail", args=(this_image.id,)))
        self.assertEqual(response.status_code, 302)


class TestLoggedOutViews(TestCase):
    def test_landing_page(self):
        response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 200)


class TestOtherViews(TestCase):
    def setUp(self):
        branch1 = create_branch("BRANCH ONE")
        branch2 = create_branch("BRANCH TWO")
        branch3 = create_branch("BRANCH THREE")
        branch4 = create_branch("BRANCH FOUR")

        self.client = Client()
        self.user = User.objects.create_user(
            "john", "lennon@thebeatles.com", "johnpassword"
        )

        self.person = create_person(display_name="Marcia Brady")

        self.profile = Profile()
        self.profile.user = self.user
        self.profile.guest_user = False
        self.profile.person = self.person
        self.profile.save()

        first_branch = Branch.objects.filter(pk=1)
        self.profile.branches.set(first_branch)
        self.profile.save()

    def test_other_views(self):
        """
        Test that index views load
        """

        self.client.login(username="john", password="johnpassword")
        response = self.client.get(reverse("person_index"))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, "No people are available.")

        response = self.client.get(reverse("family_index"))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, "No families are available.")

        response = self.client.get(reverse("image_index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No images are available.")

        response = self.client.get(reverse("video_index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No videos are available.")

        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("outline"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("account"))
        self.assertEqual(response.status_code, 200)
