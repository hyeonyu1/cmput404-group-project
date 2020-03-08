from django.test import SimpleTestCase
from django.urls import reverse, resolve
from friendship.views import send_friend_request, handle_friend_request, retrieve_friend_request_of_author_id

class TestFriendshipUrls(SimpleTestCase):

    def test_send_friend_request(self):
        url = reverse("send_friend_request")
        self.assertEqual(resolve(url).func, send_friend_request)

    def test_handle_friend_request(self):
        url = reverse("handle_friend_request")
        self.assertEqual(resolve(url).func, handle_friend_request)

    def test_retrieve_friend_request_of_author_id(self):
        url = reverse("retrieve_friend_request_of_author_id",
                      args=["01ee71da-c303-4675-a09c-46f1942dabaf"])
        self.assertEqual(resolve(url).func, retrieve_friend_request_of_author_id)
