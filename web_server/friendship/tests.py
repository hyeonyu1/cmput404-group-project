from django.test import TestCase, Client
from friendship.models import Friend, Follow, FriendRequest
from django.urls import reverse


class TestViews(TestCase):
    # Create your tests here.
    def setUp(self):
        self.client = Client()

    # test forbidden methods for http://service/friendrequest/{author_id}

    def test_retrieve_friendrequest_of_author_method_not_allowed(self):
        friend_request_retrieval_url = reverse(
            'retrieve_friend_request_of_author_id', args=['A'])
        response = self.client.post(friend_request_retrieval_url)
        self.assertTrue(response.status_code == 405)
        response = self.client.put(friend_request_retrieval_url)
        self.assertTrue(response.status_code == 405)
        response = self.client.delete(friend_request_retrieval_url)
        self.assertTrue(response.status_code == 405)

    # test forbidden methods for http://service/friendrequest/{author_id}

    def test_retrieve_friendrequest_of_author(self):
        friend_request_retrieval_url = reverse(
            'retrieve_friend_request_of_author_id', args=['A'])
        request_1 = FriendRequest(from_id="B", to_id="testserver/author/A")
        request_1.save()
        request_2 = FriendRequest(from_id="C", to_id="testserver/author/A")
        request_2.save()
        response = self.client.get(friend_request_retrieval_url)
        json_response = response.json()
        self.assertTrue(response.status_code == 200)
        self.assertEquals(json_response['query'], 'retrieve_friend_requests')
        self.assertEquals(json_response['author'], 'testserver/author/A')
        self.assertEquals(len(json_response['request']), 2)
        FriendRequest.objects.filter(from_id="B").filter(
            to_id="testserver/author/A").delete()
        FriendRequest.objects.filter(from_id="C").filter(
            to_id="testserver/author/A").delete()

    # test forbidden methods for http://service/friendrequest

    def test_send_friendrequest_method_not_allowed(self):
        send_friendrequest_url = reverse('send_friend_request')
        response = self.client.get(send_friendrequest_url)
        self.assertTrue(response.status_code == 405)
        response = self.client.put(send_friendrequest_url)
        self.assertTrue(response.status_code == 405)
        response = self.client.delete(send_friendrequest_url)
        self.assertTrue(response.status_code == 405)

    # test http://service/friendrequest
    def test_send_friendrequest(self):
        send_friendrequest_url = reverse('send_friend_request')
        post_data = {
            "query": "friendrequest",
            "author": {
                "id": "A",
                "host": "http://127.0.0.1:5454/",
                "displayName": "Greg Johnson",
                "url": "http://127.0.0.1:5454/author/de305d54-75b4-431b-adb2-eb6b9e546013",
            },
            "friend": {
                "id": "B",
                "host": "http://127.0.0.1:5454/",
                "displayName": "Lara Croft",
                "url": "http://127.0.0.1:5454/author/de305d54-75b4-431b-adb2-eb6b9e546013",

            }

        }
        response = self.client.post(send_friendrequest_url, data=post_data,
                                    content_type="application/json")
        self.assertTrue(response.status_code == 200)
        self.assertTrue(FriendRequest.objects.filter(
            from_id="A", to_id="B").exists())
        # test cleanup: delete FriendRequest Entry
        FriendRequest.objects.filter(
            from_id="A", to_id="B").delete()
