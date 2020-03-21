"""
Requirement #50
As an author, I want to be able to make posts that are unlisted, that are publicly shareable by URI alone (or for embedding images)
"""

from django.test import TestCase, Client, override_settings
from django.urls import reverse, resolve

from users.models import Author
from posts.models import Post
from friendship.models import Friend

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
            Author(username="test_user_A", email="a@gmail.com", first_name="A", last_name="A", host="127.0.0.1:8000"),
            Author(username="test_user_B", email="b@gmail.com", first_name="B", last_name="B", host="127.0.0.1:8000"),
            Author(username="test_user_C", email="c@gmail.com", first_name="C", last_name="C", host="127.0.0.1:8000"),
            Author(username="test_user_D", email="d@gmail.com", first_name="D", last_name="D", host="127.0.0.1:8000"),

            # Unsure how to test external authors now, so I'm disabling until it is clearer
            # Author(username="test_user_E", email="e@gmail.com", first_name="E", last_name="E", host="example.com"),

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

        # Create one client for each user so that they can talk to the application simultaneously
        self.a_client = Client(HTTP_ACCEPT="application/json", **self.request_headers['A'])
        self.b_client = Client(HTTP_ACCEPT="application/json", **self.request_headers['B'])
        self.c_client = Client(HTTP_ACCEPT="application/json", **self.request_headers['C'])
        self.d_client = Client(HTTP_ACCEPT="application/json", **self.request_headers['D'])
        # self.e_client = Client(HTTP_ACCEPT="application/json", **self.request_headers['E'])

        # Set up relationships between the authors
        Friends
        self.fixture_authors[0].friends.add(self.fixture_authors[1])  # A and B are friends
        self.fixture_authors[1].friends.add(self.fixture_authors[2])  # B and C are friends

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
        self.url_get_visible_posts = "/author/posts"
        self.url_get_post = lambda post_id: f"/posts/{post_id}"

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
        post_id = self.fixture_posts[0].id # the private post

        a_response = self.a_client.get(self.url_get_post(post_id), follow=True)
        b_response = self.b_client.get(self.url_get_post(post_id), follow=True)
        c_response = self.c_client.get(self.url_get_post(post_id), follow=True)
        d_response = self.d_client.get(self.url_get_post(post_id), follow=True)
        e_response = self.e_client.get(self.url_get_post(post_id), follow=True)

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

    def test_post_direct_friend(self):
        """
        Tests the friend unlisted post to see that it is only accessible by the author and friends
        """
        post_id = self.fixture_posts[1].id  # The friend post

        a_response = self.a_client.get(self.url_get_post(post_id), follow=True)
        b_response = self.b_client.get(self.url_get_post(post_id), follow=True)
        c_response = self.c_client.get(self.url_get_post(post_id), follow=True)
        d_response = self.d_client.get(self.url_get_post(post_id), follow=True)
        e_response = self.e_client.get(self.url_get_post(post_id), follow=True)

        # Check that these people can see the post
        for response in [a_response, b_response]:
            assert response.status_code == 200
            resp_json = response.json()
            assert resp_json['count'] == 1
            assert resp_json['posts'][0]['id'] == str(post_id)

        # And no one else can
        for response in [c_response, d_response, e_response]:
            assert response.status_code == 200
            resp_json = response.json()
            assert resp_json['count'] == 0
            assert len(resp_json['posts']) == 0

    def test_post_direct_foaf(self):
        """
        Tests the foaf unlisted post to see that it is only accessible by the author and foaf
        """
        post_id = self.fixture_posts[2].id  # The foaf post

        a_response = self.a_client.get(self.url_get_post(post_id), follow=True)
        b_response = self.b_client.get(self.url_get_post(post_id), follow=True)
        c_response = self.c_client.get(self.url_get_post(post_id), follow=True)
        d_response = self.d_client.get(self.url_get_post(post_id), follow=True)
        e_response = self.e_client.get(self.url_get_post(post_id), follow=True)

        # Check that these people can see the post
        for response in [a_response, b_response, c_response]:
            assert response.status_code == 200
            resp_json = response.json()
            assert resp_json['count'] == 1
            assert resp_json['posts'][0]['id'] == str(post_id)

        # And no one else can
        for response in [d_response, e_response]:
            assert response.status_code == 200
            resp_json = response.json()
            assert resp_json['count'] == 0
            assert len(resp_json['posts']) == 0

    def test_post_direct_server(self):
        """
        Tests the server only unlisted post to see that it is only accessible by everyone on the server
        """
        post_id = self.fixture_posts[3].id  # The server only post

        a_response = self.a_client.get(self.url_get_post(post_id), follow=True)
        b_response = self.b_client.get(self.url_get_post(post_id), follow=True)
        c_response = self.c_client.get(self.url_get_post(post_id), follow=True)
        d_response = self.d_client.get(self.url_get_post(post_id), follow=True)
        e_response = self.e_client.get(self.url_get_post(post_id), follow=True)

        # Check that these people can see the post
        for response in [a_response, b_response, c_response, d_response]:
            assert response.status_code == 200
            resp_json = response.json()
            assert resp_json['count'] == 1
            assert resp_json['posts'][0]['id'] == str(post_id)

        # And no one else can
        for response in [e_response]:
            assert response.status_code == 200
            resp_json = response.json()
            assert resp_json['count'] == 0
            assert len(resp_json['posts']) == 0

    def test_post_direct_public(self):
        """
        Tests the public unlisted post to see that it is accessible by everyone
        """
        post_id = self.fixture_posts[4].id  # The public post

        a_response = self.a_client.get(self.url_get_post(post_id), follow=True)
        b_response = self.b_client.get(self.url_get_post(post_id), follow=True)
        c_response = self.c_client.get(self.url_get_post(post_id), follow=True)
        d_response = self.d_client.get(self.url_get_post(post_id), follow=True)
        e_response = self.e_client.get(self.url_get_post(post_id), follow=True)

        # Check that these people can see the post
        for response in [a_response, b_response, c_response, d_response, e_response]:
            assert response.status_code == 200
            resp_json = response.json()
            assert resp_json['count'] == 1
            assert resp_json['posts'][0]['id'] == str(post_id)


    ################
    # Public Posts API tests
    # Attempts to access the post through the public posts api should fail, even if the post is public. Regardless of
    # who you are, or what your relation to the author is.
    ################

    def test_post_public_api(self):
        """
        Tests the public post api to see that no one can access the unlisted posts
        """
        a_response = self.a_client.get(self.url_public_posts, follow=True)
        b_response = self.b_client.get(self.url_public_posts, follow=True)
        c_response = self.c_client.get(self.url_public_posts, follow=True)
        d_response = self.d_client.get(self.url_public_posts, follow=True)
        e_response = self.e_client.get(self.url_public_posts, follow=True)

        # Check that no one can see the post
        for response in [a_response, b_response, c_response, d_response, e_response]:
            assert response.status_code == 200
            resp_json = response.json()
            assert resp_json['count'] == 0
            assert len(resp_json['posts']) == 0


    ################
    # Author Posts API tests
    # Attempts to access the post through the author posts api should fail, even if the post is public. Regardless of
    # who you are, or what your relation to the author is.
    ################

    def test_post_author_post_api(self):
        """
        Tests the author post api to see that no one can access the unlisted posts
        """
        a_response = self.a_client.get(self.url_get_visible_posts, follow=True)
        b_response = self.b_client.get(self.url_get_visible_posts, follow=True)
        c_response = self.c_client.get(self.url_get_visible_posts, follow=True)
        d_response = self.d_client.get(self.url_get_visible_posts, follow=True)
        e_response = self.e_client.get(self.url_get_visible_posts, follow=True)

        # Check that no one can see the post
        for response in [a_response, b_response, c_response, d_response, e_response]:
            assert response.status_code == 200
            resp_json = response.json()
            assert resp_json['count'] == 0
            assert len(resp_json['posts']) == 0



