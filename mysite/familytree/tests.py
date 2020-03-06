from django.test import TestCase
from django.urls import reverse

class PersonIndexViewTests(TestCase):

    def test(self):
        """
        If no people exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('person_index'))
        self.assertEqual(response.status_code, 200)

