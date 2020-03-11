from django.test import TestCase, Client, override_settings
from django.urls import reverse, resolve

from users.models import Author
from posts.models import Post

# In order to avoid problems if static files get references, we can use this decorator during testing to automatically
# reference static files
@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class TestPostsAPI(TestCase):

    def setUp(self):
        self.fixture_authors = [
            # Super User
            Author(username="admin", email="admin@admin.com", password="admin", first_name="admin", last_name="."),

            # Authors
            Author(username="test_user_A", email="test_a@a.com", password="pass_a", first_name="A", last_name="A"),
            Author(username="test_user_B", email="test_b@b.com", password="pass_b", first_name="B", last_name="B"),
            Author(username="test_user_C", email="test_c@c.com", password="pass_c", first_name="C", last_name="C")
        ]
        for author in self.fixture_authors:
            author.is_active = 1
            author.save()

        self.fixture_posts_public = [
            Post(title='A post 1 public', content="A1 content", author=self.fixture_authors[0]),
            Post(title='A post 2 public', content="A2 content", author=self.fixture_authors[0]),
            Post(title='A post 3 public', content="A3 content", author=self.fixture_authors[0]),

            Post(title='B post 1 public', content="B1 content", author=self.fixture_authors[1]),
            Post(title='B post 2 public', content="B2 content", author=self.fixture_authors[1]),
            Post(title='B post 3 public', content="B3 content", author=self.fixture_authors[1]),

            Post(title='C post 1 public', content="C1 content", author=self.fixture_authors[2]),
            Post(title='C post 2 public', content="C2 content", author=self.fixture_authors[2]),
            Post(title='C post 3 public', content="C3 content", author=self.fixture_authors[2]),
        ]
        for post in self.fixture_posts_public:
            post.size = 0
            post.visibility = Post.PUBLIC
            post.contentType = "text/plain"
            post.save()

        self.fixture_posts_other = [
            Post(author=self.fixture_authors[0], content="A foaf content", visibility=Post.FOAF, title='A post foaf'),
            Post(author=self.fixture_authors[0], content="A friend content", visibility=Post.FRIENDS, title='A post friends'),
            Post(author=self.fixture_authors[0], content="A private content", visibility=Post.PRIVATE, title='A post private'),
            Post(author=self.fixture_authors[0], content="A server content", visibility=Post.SERVERONLY, title='A post server'),

            Post(author=self.fixture_authors[1], content="B foaf content", visibility=Post.FOAF, title='B post foaf'),
            Post(author=self.fixture_authors[1], content="B friend content", visibility=Post.FRIENDS, title='B post friends'),
            Post(author=self.fixture_authors[1], content="B private content", visibility=Post.PRIVATE, title='B post private'),
            Post(author=self.fixture_authors[1], content="B server content", visibility=Post.SERVERONLY, title='B post server'),

            Post(author=self.fixture_authors[2], content="C foaf content", visibility=Post.FOAF, title='C post foaf'),
            Post(author=self.fixture_authors[2], content="C friend content", visibility=Post.FRIENDS, title='C post friends'),
            Post(author=self.fixture_authors[2], content="C private content", visibility=Post.PRIVATE, title='C post private'),
            Post(author=self.fixture_authors[2], content="C server content", visibility=Post.SERVERONLY, title='C post server'),
        ]
        for post in self.fixture_posts_other:
            post.size = 0
            post.contentType = 'text/plain'
            post.save()

        # Because we are testing the API document, we should NOT use reverse to get the URIs
        # Instead we should hardcode the URI's such that we ensure we are always spec compliant

        self.url_public_posts = "/posts"
        self.url_get_post = lambda post_id: f"/posts/{post_id}"

        self.client = Client(HTTP_ACCEPT="application/json")

    # Needed tests
    # service/posts
    # service/posts/{post_id}

    ################
    # Tests for service/posts
    ################

    def test_posts_get_all_public_posts(self):
        """
        Test if service/posts will return all public posts and only public posts
        """
        # Get all posts from the first page - 1 and check if everything matches with the spec
        response = self.client.get(self.url_public_posts, {
            "page": 1,
            "size": len(self.fixture_posts_public) - 1
        }, follow=True)
        assert(response.status_code == 200)
        response = response.json()
        assert(response['query'] == 'posts')
        assert(response['count'] == len(self.fixture_posts_public))
        assert(response['size'] == len(self.fixture_posts_public) - 1)
        assert("page=2" in response['next'])
        assert('prev' not in response)
        posts = Post.objects.filter(id__in=[r['id'] for r in response['posts']])
        for post in posts:
            assert(post in self.fixture_posts_public)

        # Then follow the url to the next page and see if all posts have been shown and no extras exist
        response = self.client.get(response['next'], follow=True).json()
        posts = [p for p in posts] + [p for p in Post.objects.filter(id__in=[r['id'] for r in response['posts']])]
        assert(posts == self.fixture_posts_public)

        # Check for the prev page matching the spec
        assert('page=1' in response['prev'])


    ################
    # Tests for service/posts/{post_id}
    ################
    def test_get_single_post(self):
        for post in self.fixture_posts_public:
            response = self.client.get(self.url_get_post(post['id']))
            assert response.status_code == 200
            json = response.json()
            assert Post.objects.get(pk=post['id']) == post


