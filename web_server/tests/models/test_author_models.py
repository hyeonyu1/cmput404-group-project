from django.test import TestCase

import uuid
from datetime import datetime

from web_server.users.models import Author


@override_settings(HOSTNAME="127.0.0.1")
class TestAuthorModels(TestCase):

    def setUp(self):
        id = uuid.uuid5(uuid.NAMESPACE_DNS, 'test')
        id_str = str(id)
        Author.objects.create(id = id,display_name="TestAuthorModels",email="author@test.com",password="password1", first_name="firstname",
            last_name="lastname",bio="authortest.com", github="github.com", is_active="True",host="127.0.0.1:8000", is_superuser="False",
                              is_staff="False",uid="127.0.0.1:8000/author/"+id_str,url="http://127.0.0.1:8000/author/"+id_str,
                              date_joined=datetime(year=2020, month=2, day=26))

    def test_sample(self):
        assert (1 == 1)

    def test_author_is_uid_local(self):
        id = uuid.uuid5(uuid.NAMESPACE_DNS, 'test')
        id_str = str(id)
        uid = "127.0.0.1:8000/author/" + id_str
        author_test = Author.objects.get(id = id)

        self.assertEqual(author_test.is_uid_local(uid),True)

    def test_author_extract_uuid_from_uid(self):
        id = uuid.uuid5(uuid.NAMESPACE_DNS, 'test')
        author_test = Author.objects.get(id=id)
        id_str = str(id)
        uid = "127.0.0.1:8000/author/" + id_str

        self.assertEqual(author_test.extract_uuid_from_uid(uid),id_str)

    def test_to_api_object(self):
        id = uuid.uuid5(uuid.NAMESPACE_DNS, 'test')
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

        self.assertEqual(author_test.to_api_object, testdic)