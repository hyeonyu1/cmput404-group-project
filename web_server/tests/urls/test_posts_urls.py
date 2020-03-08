from django.test import SimpleTestCase
from django.urls import reverse, resolve
from posts.views import retrieve_all_public_posts_on_local_server, retrieve_single_post_with_id, comments_retrieval_and_creation_to_post_id


class TestFriendshipUrls(SimpleTestCase):

    def test_retrieve_all_public_posts_on_local_server(self):
        url = reverse("retrieve_all_public_posts_on_local_server")
        self.assertEqual(resolve(url).func, retrieve_all_public_posts_on_local_server)

    def test_retrieve_single_post_with_id(self):
        url = reverse("retrieve_single_post_with_id",
                      args=["112fbc43-5f67-4d2f-b61b-aada16cfd6c1"])
        self.assertEqual(resolve(url).func, retrieve_single_post_with_id)

    def test_comments_retrieval_and_creation_to_post_id(self):
        url = reverse("comments_retrieval_and_creation_to_post_id",
                      args=["112fbc43-5f67-4d2f-b61b-aada16cfd6c1"])
        self.assertEqual(resolve(url).func, comments_retrieval_and_creation_to_post_id)
