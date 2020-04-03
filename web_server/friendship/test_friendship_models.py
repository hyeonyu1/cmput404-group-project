import uuid
from django.test import TestCase, Client, override_settings
from users.models import Author
from posts.models import Post
from friendship.models import Friend,FriendRequest,Follow

class TestFriendshipModels(TestCase):

    def setUp(self):
        id1 = uuid.uuid5(uuid.NAMESPACE_DNS, 'test1').hex
        id2 = uuid.uuid5(uuid.NAMESPACE_DNS, 'test2').hex
        id_str1=str(id1)
        uid1 = "127.0.0.1:8000/author/" + id_str1
        id_str2 = str(id2)
        uid2 = "127.0.0.1:8000/author/" + id_str2

        Friend.objects.create(author_id=uid1, friend_id=uid2)
        FriendRequest.objects.create(from_id=uid1, to_id=uid2)
        Follow.objects.create(follower_id=uid1,followee_id=uid2)

    def test_data(self):
        id1 = uuid.uuid5(uuid.NAMESPACE_DNS, 'test1').hex
        id2 = uuid.uuid5(uuid.NAMESPACE_DNS, 'test2').hex
        id_str1 = str(id1)
        uid1 = "127.0.0.1:8000/author/" + id_str1
        id_str2 = str(id2)
        uid2 = "127.0.0.1:8000/author/" + id_str2

        friend_test=Friend.objects.get(author_id=uid1, friend_id=uid2)
        friend_request_test=FriendRequest.objects.get(from_id=uid1, to_id=uid2)
        follow_test=Follow.objects.get(follower_id=uid1, followee_id=uid2)

        self.assertEqual(friend_test.author_id, uid1)
        self.assertEqual(friend_test.friend_id, uid2)
        self.assertEqual(friend_request_test.from_id, uid1)
        self.assertEqual(friend_request_test.to_id, uid2)
        self.assertEqual(follow_test.follower_id, uid1)
        self.assertEqual(follow_test.followee_id, uid2)





