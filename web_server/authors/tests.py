from django.test import TestCase, Client
from users.models import Author
from friendship.models import Friend
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
    # test forbidden methods for service/author/<str:author_id>/

    def test_retrieve_author_profile_method_not_allowed(self):
        # create test_author
        # 405 except GET
        response = self.client.post(self.retrieve_author_profile_url)
        self.assertTrue(response.status_code == 405)
        response = self.client.delete(self.retrieve_author_profile_url)
        self.assertTrue(response.status_code == 405)
        response = self.client.put(self.retrieve_author_profile_url)
        self.assertTrue(response.status_code == 405)

    # test for retrieving inactive author service/author/<str:author_id>/

    def test_retrieve_inactive_author_profile(self):

        # user should not be retrievalble if not active
        response = self.client.get(self.retrieve_author_profile_url)
        self.assertTrue(response.status_code == 404)

    # test for retrieving active author service/author/<str:author_id>/
    def test_retrieve_active_author_profile(self):

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
        response = self.client.get(check_if_friends_url)
        self.assertTrue(response.status_code == 200)
        json_response = response.json()
        self.assertFalse(json_response['friends'])
        self.assertEquals(json_response['query'], "friends")
        self.assertEquals(
            json_response['authors'][0], "testserver/author/de305d54-75b4-431b-adb2-eb6b9e546013")
        self.assertEquals(
            json_response['authors'][1], "127.0.0.1:5454/author/ae345d54-75b4-431b-adb2-fb6b9e547891")

    # test forbidden methods for <str:author1_id>/friends/<path:author2_id>/

    def test_friend_checking_and_retrieval_method_not_allowed(self):
        check_if_friends_url = reverse('check_if_friends', kwargs={
            'author1_id': 'de305d54-75b4-431b-adb2-eb6b9e546013', 'author2_id': '127.0.0.1:5454/author/ae345d54-75b4-431b-adb2-fb6b9e547891'})
        # 405 except GET
        response = self.client.post(check_if_friends_url)
        self.assertTrue(response.status_code == 405)
        response = self.client.put(check_if_friends_url)
        self.assertTrue(response.status_code == 405)
        response = self.client.delete(check_if_friends_url)
        self.assertTrue(response.status_code == 405)

    # test GET author/<path:author_id>/friends/

    def test_friend_checking_and_retrieval_GET(self):
        friend_checking_and_retrieval_url = reverse(
            'friend_checking_and_retrieval', args=[self.test_author.uid])
        response = self.client.get(friend_checking_and_retrieval_url)
        json_response = response.json()

        self.assertTrue(response.status_code == 200)
        # test response data entry
        self.assertEquals(json_response["query"], "friends")
        self.assertFalse(json_response["authors"])
        test_friend = Friend(author_id=self.test_author.uid,
                             friend_id="test_friend")
        test_friend.save()

        response = self.client.get(friend_checking_and_retrieval_url)
        json_response = response.json()
        self.assertTrue(json_response["authors"][0] == "test_friend")
        # clean up test data
        Friend.objects.filter(author_id=self.test_author.uid).filter(
            friend_id="test_friend").delete()

    # test POST author/<path:author_id>/friends/
    def test_friend_checking_and_retrieval_POST(self):
        friend_checking_and_retrieval_url = reverse(
            'friend_checking_and_retrieval', args=[self.test_author.uid])

        test_friend = Friend(author_id=self.test_author.uid,
                             friend_id="test_friend")
        test_friend.save()
        post_data = {
            "query": "friends",
            "authors": ["test_friend", "not_a_friend"]
        }
        response = self.client.post(
            friend_checking_and_retrieval_url, data=post_data, content_type="application/json")
        json_response = response.json()
        self.assertTrue(response.status_code == 200)
        self.assertEquals(json_response["query"], "friends")
        self.assertEquals(json_response["author"], self.test_author.uid)
        self.assertEquals(len(json_response["authors"]), 1)
        # clean up test data
        Friend.objects.filter(author_id=self.test_author.uid).filter(
            friend_id="test_friend").delete()

    # test forbidden method author/<path:author_id>/friends/

    def test_friend_checking_and_retrieval_not_allowed_method(self):
        friend_checking_and_retrieval_url = reverse(
            'friend_checking_and_retrieval', args=[self.test_author.uid])

        response = self.client.put(
            friend_checking_and_retrieval_url)
        self.assertTrue(response.status_code == 405)
        response = self.client.delete(
            friend_checking_and_retrieval_url)
        self.assertTrue(response.status_code == 405)

    # test forbidden methods for http://service/author/unfriend

    def test_unfriend_method_not_allowed(self):
        unfriend_url = reverse("unfriend")
        response = self.client.get(unfriend_url)
        self.assertTrue(response.status_code == 405)
        response = self.client.put(unfriend_url)
        self.assertTrue(response.status_code == 405)
        response = self.client.delete(unfriend_url)
        self.assertTrue(response.status_code == 405)

    # test  http://service/author/unfriend

    def test_unfriend(self):
        unfriend_url = reverse("unfriend")
        new_friend = Friend(author_id="A", friend_id="B")
        new_friend.save()

        post_data = {
            "author_id": new_friend.author_id,
            "friend_id": new_friend.friend_id
        }
        response = self.client.post(unfriend_url, data=post_data,
                                    content_type="application/json")

        self.assertTrue(response.status_code, 200)

        self.assertFalse(Friend.objects.filter(
            author_id="A", friend_id="B").exists())
        Friend.objects.filter(author_id="A").filter(friend_id="B").delete()

    # http://service/<str:author_id>/addfriend/
    def test_view_friend_candidate_method_not_allowed(self):
        view_friend_candidate_url = reverse(
            'view_friend_candidate', args=[self.test_author.id])
        response = self.client.post(view_friend_candidate_url)
        self.assertTrue(response.status_code == 405)
        response = self.client.put(view_friend_candidate_url)
        self.assertTrue(response.status_code == 405)
        response = self.client.delete(view_friend_candidate_url)
        self.assertTrue(response.status_code == 405)

    # http://service/<str:author_id>/addfriend/
    def test_view_friend_candidate(self):
        # create two test authors
        author = Author(username="B", email="dummy@gmail.com",
                        password="password", first_name="testing", last_name="testing", is_active=1)
        author.uid = "testserver/author/" + str(author.id)
        author.save()
        author2 = Author(username="C", email="dummy@gmail.com",
                         password="password", first_name="testing", last_name="testing", is_active=1)
        author2.uid = "testserver/author/" + str(author2.id)
        author2.save()

        view_friend_candidate_url = reverse(
            'view_friend_candidate', args=[author.id])

        response = self.client.get(view_friend_candidate_url)
        json_response = response.json()
        self.assertTrue(response.status_code == 200)
        self.assertTrue(
            json_response["available_authors_to_befriend"][0] == author2.uid)
        # friend author with author2
        new_friend1 = Friend(author_id=author.uid, friend_id=author2.uid)
        new_friend1.save()

        response = self.client.get(view_friend_candidate_url)
        json_response = response.json()
        self.assertTrue(response.status_code == 200)
        self.assertTrue(
            len(json_response["available_authors_to_befriend"]) == 0)
        # clean up test data
        Friend.objects.filter(author_id=author.uid).filter(
            friend_id=author2.uid).delete()
        Author.objects.filter(username="B").delete()
        Author.objects.filter(username="C").delete()

    def tearDown(self):
        Author.objects.filter(username="test_retrieve_author_profile").delete()
