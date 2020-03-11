from django.test import TestCase, Client
from users.models import Author
from django.urls import reverse


class TestViews(TestCase):
    def setUp(self):

        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.client = Client()

    def test_user_signup(self):
        new_user_information = {
            "username": "aNewUserForTesting",
            "email": "aNewUserForTesting@gmail.com",
            "password1": "aPassword!",
            "password2": "aPassword!",
            "first_name": "firstname",
            "last_name": "lastname",

        }
        response = self.client.post(
            self.register_url, data=new_user_information)
        # check response code
        self.assertEquals(response.status_code, 302)
        self.assertTrue(Author.objects.filter(
            username="aNewUserForTesting").exists())
        new_user = Author.objects.get(username="aNewUserForTesting")
        self.assertEquals(new_user.first_name, "firstname")
        self.assertEquals(new_user.last_name, "lastname")
        self.assertEquals(new_user.email, "aNewUserForTesting@gmail.com")

        self.assertTrue(new_user.uid)
        self.assertFalse(new_user.is_active)
        self.assertTrue(new_user.id)
        self.assertEquals(new_user.uid, new_user.url)
        Author.objects.get(username="aNewUserForTesting").delete()
