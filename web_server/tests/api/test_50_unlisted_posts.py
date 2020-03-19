"""
Requirement #50
As an author, I want to be able to make posts that are unlisted, that are publicly shareable by URI alone (or for embedding images)
"""

from django.test import TestCase, Client, override_settings
from django.urls import reverse, resolve

from users.models import Author
from posts.models import Post

from base64 import b64encode

# In order to avoid problems if static files get references, we can use this decorator during testing to automatically
# reference static files
@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class TestUnlistedPosts(TestCase):

    def setUp(self):
        """
        A will have the unlisted post
        B will be A's friend
        C will be B's friend
        D is an unrelated stranger on the local server
        E is an unrelated stranger on a remote server

        None of them should be able to see the post in the public or stream apis

        """
        self.fixture_authors = [
            Author(username="test_user_A", email="a@gmail.com", first_name="A", last_name="A"),
            Author(username="test_user_B", email="b@gmail.com", first_name="B", last_name="B"),
            Author(username="test_user_C", email="c@gmail.com", first_name="C", last_name="C"),
            Author(username="test_user_D", email="d@gmail.com", first_name="D", last_name="D"),
            Author(username="test_user_E", email="e@gmail.com", first_name="E", last_name="E"),

            # Super User
            Author(username="admin", email="admin@admin.com", first_name="admin", last_name="."),

        ]
        self.request_headers = dict()

        for author in self.fixture_authors:
            author.is_active = 1
            author.calculate_uid()  # Ensures we have unique uuids for the authors
            author.set_password("password")  # the password must be hashed or checks against the password will fail
            author.save()

            # Create authorization headers so that we can request as a specific individuals during the testing
            self.request_headers[author.first_name] = {
                "HTTP_AUTHORIZATION": "Basic " + str(b64encode(bytes(author.username + ':password', 'UTF-8')), 'UTF-8')
            }

        self.fixture_posts = [
            Post(content="Unlisted private content", visibility=Post.PRIVATE, title='Unlisted post private'),
            Post(content="Unlisted friend content", visibility=Post.FRIENDS, title='Unlisted post friends'),
            Post(content="Unlisted foaf content", visibility=Post.FOAF, title='Unlisted post foaf'),
            Post(content="Unlisted server content", visibility=Post.SERVERONLY, title='Unlisted post server'),
            Post(content="Unlisted public content", visibility=Post.PUBLIC, title='Unlisted post foaf'),
        ]
        for post in self.fixture_posts:
            post.author = self.fixture_authors[0]
            post.size = 0
            post.contentType = "text/plain"
            post.unlisted = True
            post.save()

        # Because we are testing the API document, we should NOT use reverse to get the URIs
        # Instead we should hardcode the URI's such that we ensure we are always spec compliant

        self.url_public_posts = "/posts"
        self.url_get_visible_posts = "author/posts"
        self.url_get_post = lambda post_id: f"/posts/{post_id}"

        self.client = Client(HTTP_ACCEPT="application/json")

    def tearDown(self):
        for post in self.fixture_posts:
            post.delete()
        for author in self.fixture_authors:
            author.delete()

    ################
    # Direct access tests
    # If the post is accessed directly, it's visibility should be the same as if it wasn't unlisted.
    #   You can see your own posts
    #   Friends can see the post if FRIENDS set
    #   Friends, FOAF can see the post if FOAF set
    #   Anyone on local server can see the post if SERVERONLY set
    #   Anyone can see if PUBLIC is set
    ################

    def test_post_direct_private(self):
        """
        Tests the private unlisted post to see that only the author (A) can access it
        """
        a_response = self.client.get(self.url_get_post(self.fixture_posts[0].id), follow=True, **self.request_headers['A'])
        b_response = self.client.get(self.url_get_post(self.fixture_posts[0].id), follow=True, **self.request_headers['B'])
        c_response = self.client.get(self.url_get_post(self.fixture_posts[0].id), follow=True, **self.request_headers['C'])
        d_response = self.client.get(self.url_get_post(self.fixture_posts[0].id), follow=True, **self.request_headers['D'])
        e_response = self.client.get(self.url_get_post(self.fixture_posts[0].id), follow=True, **self.request_headers['E'])

        # A can view their own unlisted private post
        assert a_response.status_code == 200
        a_json = a_response.json()
        assert a_json['count'] == 1
        assert a_json['posts'][0]['id'] == str(self.fixture_posts[0].id)

        for response in [b_response, c_response, d_response, e_response]:
            # And no one else can
            assert response.status_code == 200
            resp_json = response.json()
            assert resp_json['count'] == 0
            assert len(resp_json['posts']) == 0

    # def test_post_direct_friend(self):
    #     """
    #     Tests the private unlisted post to see that only the author (A) can access it
    #     """
    #     a_response = self.client.get(self.url_get_post(self.fixture_posts[0].id), **self.request_headers['A']).json()
    #     b_response = self.client.get(self.url_get_post(self.fixture_posts[0].id), **self.request_headers['B']).json()
    #     c_response = self.client.get(self.url_get_post(self.fixture_posts[0].id), **self.request_headers['C']).json()
    #     d_response = self.client.get(self.url_get_post(self.fixture_posts[0].id), **self.request_headers['D']).json()
    #     e_response = self.client.get(self.url_get_post(self.fixture_posts[0].id), **self.request_headers['E']).json()
    #
    #     # A can view their own unlisted private post
    #     assert a_response['size'] == 1
    #     assert a_response['posts'][0].id
    #
    #     for response in [b_response, c_response, d_response, e_response]:
    #         # And no one else can
    #         assert response['size'] == 0
    #         assert len(response['posts']) == 0


    ################
    # Tests for service/posts
    ################

    # def test_posts_get_all_public_posts(self):
    #     """
    #     Test if service/posts will return all public posts and only public posts
    #     """
    #     # Get all posts from the first page - 1 and check if everything matches with the spec
    #     response = self.client.get(self.url_public_posts, {
    #         "page": 1,
    #         "size": len(self.fixture_posts_public) - 1
    #     }, follow=True)
    #     assert(response.status_code == 200)
    #     response = response.json()
    #     assert response['query'] == 'posts'
    #     assert response['count'] == len(self.fixture_posts_public)
    #     assert response['size'] == len(self.fixture_posts_public) - 1
    #     assert "page=2" in response['next']
    #     assert 'prev' not in response
    #     first_page_posts = Post.objects.filter(id__in=[r['id'] for r in response['posts']])
    #     for post in first_page_posts:
    #         assert post in self.fixture_posts_public
    #
    #     # Then follow the url to the next page and see if all posts have been shown and no extras exist
    #     response = self.client.get(response['next'], follow=True).json()
    #     all_posts = [p for p in first_page_posts] + \
    #                 [p for p in Post.objects.filter(id__in=[r['id'] for r in response['posts']])]
    #     for post in self.fixture_posts_public:
    #         assert post in all_posts
    #
    #     # Check for the prev page matching the spec
    #     assert 'page=1' in response['prev']



