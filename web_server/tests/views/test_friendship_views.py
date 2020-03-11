from django.test import TestCase, Client
from django.urls import reverse, resolve


class TestFriendshipViews(TestCase):

    def setUp(self):
        self.client = Client

    def test_sample(self):
        assert(1 == 1)
