from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Author
# this form is for user sign up


class UserRegisterForm(UserCreationForm):

    first_name = forms.CharField(
        label="firstname", max_length=30, required=True)
    last_name = forms.CharField(
        label="lastname", max_length=150, required=True)
    display_name = forms.CharField(
        label="displayname", max_length=256, required=False, help_text="optional"
    )
    email = forms.EmailField(label="email", required=True)

    bio = forms.CharField(label="bio", required=False, help_text="optional")

    github = forms.URLField(
        label="github", required=False, help_text="optional")

    class Meta:
        model = Author
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name',
                  'display_name', 'bio', 'github']


class UserChangeForm(UserChangeForm):

    class Meta:
        model = Author
        fields = ['username', 'password', 'url', 'uid', 'first_name', 'last_name',
                  'display_name', 'email', 'github', 'bio', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions']
