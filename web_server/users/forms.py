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
        label="displayname", max_length=256, required=True
    )
    email = forms.EmailField()

    class Meta:
        model = Author
        fields = ['username', 'first_name', 'last_name',
                  'display_name', 'email', 'password1', 'password2']


class UserChangeForm(UserChangeForm):

    class Meta:
        model = Author
        fields = ['username', 'first_name', 'last_name',
                  'display_name', 'email']
