from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# this form is for user sign up


class UserRegisterForm(UserCreationForm):

    first_name = forms.CharField(
        label="firstname", max_length=30, required=True)
    last_name = forms.CharField(
        label="lastname", max_length=150, required=True)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password1', 'password2']
