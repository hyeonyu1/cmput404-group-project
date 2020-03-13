from django.test import TestCase, Client, RequestFactory
from users.models import Author
from friendship.models import Friend
from posts.models import Post
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
        check_if_friends_url = reverse('check_if_two_authors_are_friends', kwargs={
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
        check_if_friends_url = reverse('check_if_two_authors_are_friends', kwargs={
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
            'friend_checking_and_retrieval_of_author_id', args=[self.test_author.uid])
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
            'friend_checking_and_retrieval_of_author_id', args=[self.test_author.uid])

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
            'friend_checking_and_retrieval_of_author_id', args=[self.test_author.uid])

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
            'view_list_of_available_authors_to_befriend', args=[self.test_author.id])
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
            'view_list_of_available_authors_to_befriend', args=[author.id])

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


    # http://service/author/posts
    def test_posts_visible_to_auth_user(self):
        author1 = Author(username="test", email="test@test.com",
                              password="password", first_name="test", last_name="test", host="testserver", is_active=1)
        author1.uid = "testserver/author/" + str(author1.id)
        author1.save()
        author2 = Author(username="posts", email="posts@posts.com",
                              password="password", first_name="post", last_name="post", host="testserver", is_active=1)
        author2.uid = "testserver/author/" + str(author2.id)
        author2.save()
        author3 = Author(username="post_friend", email="post_friend@post_friend.com",
                              password="password", first_name="post_friend", last_name="post_friend", host="testserver", is_active=1)
        author3.uid = "testserver/author/" + str(author3.id)
        author3.save()
        friendship = [
            # author1 and author2 are friends
            Friend(author_id=author1.uid, friend_id=author2.uid),
            Friend(author_id=author2.uid, friend_id=author1.uid),
            # author2 and author3 are friends
            Friend(author_id=author2.uid, friend_id=author3.uid),
            Friend(author_id=author3.uid, friend_id=author2.uid),
        ]

        for friends in friendship:
            friends.save()

        author1_private = Post(author=author1, content="private post created by test", visibility=Post.PRIVATE,
                 title='private post')
        author1_private.size = 1
        author1_private.contentType = 'text/plain'
        author1_private.save()

        # posts created by author2
        author2_friends = Post(author=author2, content="friends post created by author2", visibility=Post.FRIENDS,
                 title='friends post')
        author2_friends.size = 1
        author2_friends.contentType = 'text/plain'
        author2_friends.save()

        author2_private = Post(author=author2, content="private post created by author2 not visible to test",
                 visibility=Post.PRIVATE,
                 title='private post not visible')
        author2_private.size = 1
        author2_private.contentType = 'text/plain'
        author2_private.save()

        # post created by author3
        author3_foaf =  Post(author=author3, content="fofa post created by author3", visibility=Post.FOAF, title='foaf post')
        author3_foaf.size = 1
        author3_foaf.contentType = 'text/plain'
        author3_foaf.save()

        viewable_post = [author3_foaf, author2_friends, author1_private]
        post_id = []
        for post in viewable_post:
            post_id.append(str(post.id))

        self.client = Client(HTTP_ACCEPT="application/json")
        self.client.force_login(author1)

        response = self.client.get('/author/posts/')

        self.assertEqual(200, response.status_code)

        json_data = response.json()

        self.assertEquals(json_data['query'], 'posts')
        self.assertEquals(json_data['count'], len(viewable_post))
        self.assertEquals(json_data['size'], 10)

        returned_post_id = []
        for each_post in json_data['posts']:
            returned_post_id.append(each_post['id'])

        self.assertEqual(post_id, returned_post_id)
        Post.objects.filter(author=author1).delete()
        Post.objects.filter(author=author2).delete()
        Post.objects.filter(author=author3).delete()
        Author.objects.filter(username="test").delete()
        Author.objects.filter(username="posts").delete()
        Author.objects.filter(username="post_friend").delete()


    def test_fail_invalid_author_id_posts_visible_to_auth_user(self):
        author1 = Author(username="test", email="test@test.com",
                         password="password", first_name="test", last_name="test", host="testserver", is_active=1)
        author1.uid = "testserver/author/" + str(author1.id)
        author1.save()
        self.client = Client(HTTP_ACCEPT="application/json")
        self.client.force_login(author1)
        view_post_of_author = reverse('retrieve_posts_of_author_id_visible_to_current_auth_user', args=[1])
        response = self.client.get(view_post_of_author)

        self.assertEqual(404, response.status_code)

    # http://service/author/{author_id}/posts
    def test_author_id_posts_visible_to_auth_user(self):
        author1 = Author(username="test", email="test@test.com",
                         password="password", first_name="test", last_name="test", host="testserver", is_active=1)
        author1.uid = "testserver/author/" + str(author1.id)
        author1.save()
        author2 = Author(username="posts", email="posts@posts.com",
                         password="password", first_name="post", last_name="post", host="testserver", is_active=1)
        author2.uid = "testserver/author/" + str(author2.id)
        author2.save()
        author3 = Author(username="post_friend", email="post_friend@post_friend.com",
                         password="password", first_name="post_friend", last_name="post_friend", host="testserver",
                         is_active=1)
        author3.uid = "testserver/author/" + str(author3.id)
        author3.save()
        friendship = [
            # author1 and author2 are friends
            Friend(author_id=author1.uid, friend_id=author2.uid),
            Friend(author_id=author2.uid, friend_id=author1.uid),
            # author2 and author3 are friends
            Friend(author_id=author2.uid, friend_id=author3.uid),
            Friend(author_id=author3.uid, friend_id=author2.uid),
        ]
        for friends in friendship:
            friends.save()

        # posts created by author2
        author2_friends = Post(author=author2, content="friends post created by author2", visibility=Post.FRIENDS,
                               title='friends post')
        author2_friends.size = 1
        author2_friends.contentType = 'text/plain'
        author2_friends.save()
        author2_public = Post(author=author2, content="public post created by author2", visibility=Post.PUBLIC,
                               title='public post')
        author2_public.size = 1
        author2_public.contentType = 'text/plain'
        author2_public.save()

        author2_private = Post(author=author2, content="private post created by author2 not visible to test",
                               visibility=Post.PRIVATE,
                               title='private post')
        author2_private.visibleTo.set([author1.uid])
        author2_private.size = 1
        author2_private.contentType = 'text/plain'
        author2_private.save()

        # post created by author3
        author3_foaf = Post(author=author3, content="fofa post created by author3", visibility=Post.FOAF,
                            title='foaf post')
        author3_foaf.size = 1
        author3_foaf.contentType = 'text/plain'
        author3_foaf.save()
        author3_private = Post(author=author3, content="private post created by author3", visibility=Post.PRIVATE,
                            title='privage post')
        author3_private.size = 1
        author3_private.contentType = 'text/plain'
        author3_private.save()

        self.client = Client(HTTP_ACCEPT="application/json")
        self.client.force_login(author1)

        viewable_post_for_author3 = [author3_foaf]
        viewable_post_for_author2 = [author2_private, author2_public, author2_friends]

        post_id_author3 = []
        post_id_author2 = []

        for post in viewable_post_for_author3:
            post_id_author3.append(str(post.id))

        for post in viewable_post_for_author2:
            post_id_author2.append(str(post.id))


        view_post_of_author2 = reverse('retrieve_posts_of_author_id_visible_to_current_auth_user', args=[author2.id])
        view_post_of_author3 = reverse('retrieve_posts_of_author_id_visible_to_current_auth_user', args=[author3.id])

        response = self.client.get(view_post_of_author2)

        self.assertEqual(200, response.status_code)

        # getting json
        json_data = response.json()

        self.assertEquals(json_data['query'], 'posts')
        self.assertEquals(json_data['count'], len(viewable_post_for_author2))
        self.assertEquals(json_data['size'], 10)

        returned_post_id = []
        for each_post in json_data['posts']:
            returned_post_id.append(each_post['id'])

        self.assertEqual(post_id_author2, returned_post_id)

        response = self.client.get(view_post_of_author3)

        self.assertEqual(200, response.status_code)

        # getting json
        json_data = response.json()

        self.assertEquals(json_data['query'], 'posts')
        self.assertEquals(json_data['count'], len(viewable_post_for_author3))
        self.assertEquals(json_data['size'], 10)

        returned_post_id = []
        for each_post in json_data['posts']:
            returned_post_id.append(each_post['id'])

        self.assertEqual(post_id_author3, returned_post_id)

        Post.objects.filter(author=author1).delete()
        Post.objects.filter(author=author2).delete()
        Post.objects.filter(author=author3).delete()
        Author.objects.filter(username="test").delete()
        Author.objects.filter(username="posts").delete()
        Author.objects.filter(username="post_friend").delete()

    # < str: author_id > / update
    def test_profile_update(self):
        author = Author(username="test", email="test@test.com",
                        password="password", first_name="test", last_name="test", is_active=1)
        author.uid = "testserver/author/" + str(author.id)
        author.save()

        self.client = Client(HTTP_ACCEPT="application/json")
        self.client.force_login(author)
        profile = reverse("update_author_profile", args=[author.id])

        response = self.client.post(profile, {'first_name': 'test',
                                                'last_name': 'test',
                                                'email': 'test@test.com',
                                                'bio': 'updated',
                                                'github': '',
                                                'display_name': '',
                                                'delete': False}, content_type="application/json")
        author.refresh_from_db()
        self.assertEquals(response.status_code, 200)

        self.assertEquals(author.first_name, 'test')
        self.assertEquals(author.bio, 'updated')

        Author.objects.filter(username='test').delete()

    def test_delete(self):
        author = Author(username="test", email="test@test.com",
                        password="password", first_name="test", last_name="test", is_active=1)
        author.uid = "testserver/author/" + str(author.id)
        author.save()

        self.client = Client(HTTP_ACCEPT="application/json")
        self.client.force_login(author)
        profile = reverse("update_author_profile", args=[author.id])

        response = self.client.post(profile, {'first_name': 'test',
                                              'last_name': 'test',
                                              'email': 'test@test.com',
                                              'bio': '',
                                              'github': '',
                                              'display_name': '',
                                              'delete': True}, content_type="application/json")
        self.assertEquals(response.status_code, 200)

        self.assertEquals(Author.objects.filter(username='test').exists(), False)

    def test_fail_delete(self):
        author = Author(username="test", email="test@test.com",
                        password="password", first_name="test", last_name="test", is_active=1)
        author.uid = "testserver/author/" + str(author.id)
        author.save()

        self.client = Client(HTTP_ACCEPT="application/json")
        self.client.force_login(author)
        profile = reverse("update_author_profile", args=[author.id])
        response = self.client.post(profile, {'first_name': 'test',
                                              'last_name': 'test',
                                              'email': 'test@test.com',
                                              'bio': '',
                                              'github': '',
                                              'delete': False}, content_type="application/json")
        self.assertEquals(response.status_code, 404)


    def tearDown(self):
        Author.objects.filter(username="test_retrieve_author_profile").delete()



