from django.test import SimpleTestCase
from django.urls import reverse, resolve
from users.views import register, profile, mandala, CustomLogin
from django.contrib.auth import views as auth_views


class TestFriendshipUrls(SimpleTestCase):

    def test_register(self):
        url = reverse("register")
        self.assertEqual(resolve(url).func, register)

    def test_profile(self):
        url = reverse("profile")
        self.assertEqual(resolve(url).func, profile)

    def test_mandala(self):
        url = reverse("mandala")
        self.assertEqual(resolve(url).func, mandala)

    def test_login(self):
        url = reverse("login")
        self.assertEqual(resolve(url).func.view_class, CustomLogin)

    def test_logout(self):
        url = reverse("logout")
        self.assertEqual(resolve(url).func.view_class, auth_views.LogoutView)
