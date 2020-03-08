from django.test import TestCase, Client
from users.models import Author
from django.urls import reverse


class TestViews(TestCase):
    def setUp(self):
        self.test_author = Author(username="test_retrieve_author_profile", email="dummy@gmail.com",
                                  password="password", first_name="testing", last_name="testing", is_active=0)
        self.test_author.uid = "testserver/author/" + self.test_author.id.hex
        self.test_author.save()
        self.retrieve_author_profile_url = reverse(
            'retrieve_author_profile', args=[self.test_author.id.hex])
        # sample test data: http://service/author/de305d54-75b4-431b-adb2-eb6b9e546013/friends/127.0.0.1:5454/author/ae345d54-75b4-431b-adb2-fb6b9e547891

        self.client = Client()
    # test for service/author/<str:author_id>/

    def test_retrieve_author_profile(self):
        # create test_author
        # 405 except GET
        response = self.client.post(self.retrieve_author_profile_url)
        self.assertTrue(response.status_code == 405)
        # user should not be retrievalble if not active
        response = self.client.get(self.retrieve_author_profile_url)
        self.assertTrue(response.status_code == 404)
        self.test_author.is_active = 1
        self.test_author.save()
        response = self.client.get(self.retrieve_author_profile_url)

        self.assertTrue(response.status_code == 200)
        json_response = response.json()

        self.assertEquals(json_response['id'], self.test_author.uid)
        self.assertEquals(json_response['firstName'], "testing")
        self.assertEquals(json_response['firstName'], "testing")
        self.assertEquals(json_response['lastName'], "testing")
        self.assertEquals(json_response['email'], "dummy@gmail.com")

    # test for <str:author1_id>/friends/<path:author2_id>/
    def test_friend_checking_and_retrieval(self):
        check_if_friends_url = reverse('check_if_friends', kwargs={
            'author1_id': 'de305d54-75b4-431b-adb2-eb6b9e546013', 'author2_id': '127.0.0.1:5454/author/ae345d54-75b4-431b-adb2-fb6b9e547891'})
        # 405 except GET
        response = self.client.post(check_if_friends_url)
        self.assertTrue(response.status_code == 405)
        # user should not be retrievalble if not active
        response = self.client.get(check_if_friends_url)
        self.assertTrue(response.status_code == 200)
        json_response = response.json()
        self.assertFalse(json_response['friends'])
        self.assertEquals(json_response['query'], "friends")
        self.assertEquals(
            json_response['authors'][0], "testserver/author/de305d54-75b4-431b-adb2-eb6b9e546013")
        self.assertEquals(
            json_response['authors'][1], "127.0.0.1:5454/author/ae345d54-75b4-431b-adb2-fb6b9e547891")

    # test author/<str:author_id>/friends/
    def test_friend_checking_and_retrieval(self):
        friend_checking_and_retrieval_url = reverse(
            'friend_checking_and_retrieval', args=[self.test_author.id.hex])

        print(friend_checking_and_retrieval_url)
