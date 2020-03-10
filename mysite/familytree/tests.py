from django.test import TestCase
from django.urls import reverse
from .models import Person, Family, Image


class PersonModelTests(TestCase):

    def test_unreviewed_person(self):
        """
        unreviewed_person() returns True for person whose reviewed flag is False
        """
        unreviewed_person = Person(reviewed=False)
        self.assertIs(unreviewed_person.unreviewed_person(), True)

class FamilyModelTests(TestCase):

    def test_unreviewed_family(self):
        """
        unreviewed_family() returns True for family whose reviewed flag is False
        """
        unreviewed_family = Family(reviewed=False)
        self.assertIs(unreviewed_family.unreviewed_family(), True)


class IndexViewTests(TestCase):

    def test_index_views(self):
        """
        Test that index views load
        """
        response = self.client.get(reverse('person_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No people are available.")

        response = self.client.get(reverse('family_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No families are available.")

        response = self.client.get(reverse('image_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No images are available.")

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)


class DetailViewTests(TestCase):

    def test_person_detail_view(self):
        """
        Test that person detail view loads
        """
        this_person = create_person(display_name="Marcia Brady")
        response = self.client.get(reverse('person_detail', args=(this_person.id,)))
        self.assertEqual(response.status_code, 200)

    def test_family_detail_view(self):
        """
        Test that family detail view loads
        """
        wife = create_person(display_name="Carol Brady")
        husband = create_person(display_name="Mike Brady")
        this_family = create_family(display_name="The Bradys (Mike & Carol)", wife = wife, husband=husband)
        response = self.client.get(reverse('family_detail', args=(this_family.id,)))
        self.assertEqual(response.status_code, 200)
        #


    def test_image_detail_view(self):
        """
        Test that image detail view loads
        """
        this_image = create_image(big_name="blah.jpg")
        response = self.client.get(reverse('image_detail', args=(this_image.id,)))
        self.assertEqual(response.status_code, 200)

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