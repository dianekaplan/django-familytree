import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.mysite.settings")

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

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


def create_profile(user):
    """
    Create a profile for the given user
    """
    return Profile.objects.create(user=user)


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
        this_family = create_family(display_name="The Bradys (Mike & Carol)", wife=wife, husband=husband)
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
        create_branch("BRANCH ONE")
        create_branch("BRANCH TWO")
        create_branch("BRANCH THREE")
        create_branch("BRANCH FOUR")

        self.client = Client()
        self.user = User.objects.create_user("john", "lennon@thebeatles.com", "johnpassword")

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

        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

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

        response = self.client.get(reverse("outline"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("history"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("account"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("user_metrics"))
        self.assertEqual(response.status_code, 200)


def test_image_detail_with_images_param(self):
    # create two images
    img1 = create_image(big_name="one.jpg")
    img2 = create_image(big_name="two.jpg")

    # login
    self.client.login(username="jane", password="janepass")

    # request image detail with images param
    url = reverse("image_detail", args=(img1.id,)) + "?images=%d,%d" % (img1.id, img2.id)
    response = self.client.get(url)

    # should render the page
    self.assertEqual(response.status_code, 200)

    # context should include ordered images
    images_ctx = response.context.get("images")
    self.assertIsNotNone(images_ctx)
    self.assertEqual(len(images_ctx), 2)
    self.assertEqual(images_ctx[0].id, img1.id)
    self.assertEqual(images_ctx[1].id, img2.id)

    # thumbnails markup should include the image filenames
    content = response.content.decode("utf-8")
    self.assertIn("one.jpg", content)
    self.assertIn("two.jpg", content)
