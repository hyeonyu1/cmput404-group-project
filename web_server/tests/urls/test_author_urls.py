from django.test import SimpleTestCase
from django.urls import reverse, resolve
from authors.views import view_list_of_available_authors_to_befriend, unfriend, update_author_profile, retrieve_author_profile, post_creation_and_retrival_to_curr_auth_user, retrieve_posts_of_author_id_visible_to_current_auth_user, friend_checking_and_retrieval_of_author_id, check_if_two_authors_are_friends, post_edit_and_delete


class TestAuthorUrls(SimpleTestCase):

    def test_post_creation_and_retrieval_to_curr_auth_user(self):
        url = reverse("add_or_get_post")
        self.assertEqual(resolve(url).func, post_creation_and_retrival_to_curr_auth_user)

    def test_post_edit_and_delete(self):
        url = reverse("edit_or_delete_post")
        self.assertEqual(resolve(url).func, post_edit_and_delete)


    def test_retrieve_posts_of_author_id_visible_to_current_auth_user(self):
        url = reverse("retrieve_posts_of_author_id_visible_to_current_auth_user",
                      args=["01ee71da-c303-4675-a09c-46f1942dabaf"])
        self.assertEqual(resolve(url).func, retrieve_posts_of_author_id_visible_to_current_auth_user)

    def test_friend_checking_and_retrieval_of_author_id(self):
        url = reverse("friend_checking_and_retrieval_of_author_id",
                      args=["01ee71da-c303-4675-a09c-46f1942dabaf"])
        self.assertEqual(resolve(url).func, friend_checking_and_retrieval_of_author_id)

    def test_check_if_two_authors_are_friends(self):
        url = reverse("check_if_two_authors_are_friends",
                      args=["01ee71da-c303-4675-a09c-46f1942dabaf", "06eb7efb-ec4f-4efe-be1c-66b9b43f524b"])
        self.assertEqual(resolve(url).func, check_if_two_authors_are_friends)

    def test_retrieve_author_profile(self):
        url = reverse("retrieve_author_profile",
                      args=["01ee71da-c303-4675-a09c-46f1942dabaf"])
        self.assertEqual(resolve(url).func, retrieve_author_profile)

    def test_update_author_profile(self):
        url = reverse("update_author_profile",
                      args=["01ee71da-c303-4675-a09c-46f1942dabaf"])
        self.assertEqual(resolve(url).func, update_author_profile)

    def test_unfriend(self):
        url = reverse("unfriend")
        self.assertEqual(resolve(url).func, unfriend)

    def test_view_list_of_available_authors_to_befriend(self):
        url = reverse("view_list_of_available_authors_to_befriend",
                      args=["01ee71da-c303-4675-a09c-46f1942dabaf"])
        self.assertEqual(resolve(url).func, view_list_of_available_authors_to_befriend)


