from django.test import TestCase, Client
from users.models import Author
from django.urls import reverse


class TestViews(TestCase):
    def setUp(self):
        test_author = Author(username="test_retrieve_author_profile", email="dummy@gmail.com",
                             password="password", first_name="testing", last_name="testing", is_active=1)
        test_author.uid = "localhost:8000/author/" + test_author.id.hex
        test_author.save()
        self.retrieve_author_profile_url = reverse(
            'retrieve_author_profile', args=[test_author.id.hex])

        self.client = Client()

    def test_retrieve_author_profile(self):
        # create test_author
        print(self.retrieve_author_profile_url)
        response = self.client.get(self.retrieve_author_profile_url)
        print(response.content)
