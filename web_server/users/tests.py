import uuid
from datetime import datetime

from django.test import TestCase, Client, override_settings
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


#This is the unit test for author model
@override_settings(HOSTNAME="127.0.0.1:8000")
class TestAuthorModels(TestCase):

    def setUp(self):
        id = uuid.uuid5(uuid.NAMESPACE_DNS, 'test').hex
        id_str = str(id)
        Author.objects.create(id = id,display_name="TestAuthorModels",email="author@test.com",password="password1", first_name="firstname",
            last_name="lastname",bio="authortest.com", github="github.com", is_active=True,host="127.0.0.1:8000", is_superuser=False,
                              is_staff="False",uid="127.0.0.1:8000/author/"+id_str,url="http://127.0.0.1:8000/author/"+id_str,
                              date_joined=datetime(year=2020, month=2, day=26))



    def test_data(self):
        id = uuid.uuid5(uuid.NAMESPACE_DNS, 'test').hex
        id_str = str(id)
        display_name = "TestAuthorModels"
        email = "author@test.com"
        password = "password1"
        first_name = "firstname"
        last_name = "lastname"
        bio = "authortest.com"
        github = "github.com"
        is_active = True
        host = "127.0.0.1:8000"
        is_superuser = False
        is_staff = False
        uid = "127.0.0.1:8000/author/" + id_str
        url = "http://127.0.0.1:8000/author/" + id_str,
        date_joined = datetime(year=2020, month=2, day=26)

        author_test = Author.objects.get(id=id)


    def test_author_is_uid_local(self):
        id = uuid.uuid5(uuid.NAMESPACE_DNS, 'test').hex
        id_str = str(id)
        uid = "127.0.0.1:8000/author/" + id_str
        author_test = Author.objects.get(id = id)

        self.assertEqual(author_test.is_uid_local(uid),True)

    def test_author_extract_uuid_from_uid(self):
        id = uuid.uuid5(uuid.NAMESPACE_DNS, 'test').hex
        author_test = Author.objects.get(id=id)
        id_str = str(id)
        uid = "127.0.0.1:8000/author/" + id_str

        self.assertEqual(author_test.extract_uuid_from_uid(uid), id_str)

    def test_to_api_object(self):
        id = uuid.uuid5(uuid.NAMESPACE_DNS, 'test').hex
        author_test = Author.objects.get(id=id)
        id_str = str(id)
        uid = "127.0.0.1:8000/author/" + id_str
        host = "127.0.0.1:8000"
        display_name = "TestAuthorModels"
        github = "github.com"
        testdic = {
            "id": uid,
            "host": host,
            "displayName": display_name,
            "url": uid,
            "github": github
        }

        returndict = author_test.to_api_object()
        self.assertEqual(returndict['id'], testdic['id'])
        self.assertEqual(returndict['host'], testdic['host'])
        self.assertEqual(returndict['displayName'], testdic['displayName'])
        self.assertEqual(returndict['url'], testdic['url'])
        self.assertEqual(returndict['github'], testdic['github'])

