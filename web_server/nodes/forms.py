from django import forms
from .models import Node
from django.contrib.auth.password_validation import validate_password


class ForeignServerRegisterForm(forms.ModelForm):

    foreign_server_hostname = forms.CharField(
        label="foreign_server_hostname", required=True, max_length=500)
    foreign_server_username = forms.CharField(
        label="foreign_server_username", required=True, max_length=500)
    foreign_server_password = forms.CharField(
        label="foreign_server_password", max_length=30, required=True, widget=forms.PasswordInput, validators=[validate_password])
    foreign_server_api_location = forms.CharField(
        label="foreign_server_api_location", max_length=500, required=True)

    username_registered_on_foreign_server = forms.CharField(
        label="username_registered_on_foreign_server", max_length=500, required=False, help_text="optional"
    )
    password_registered_on_foreign_server = forms.CharField(
        label="password_registered_on_foreign_server", max_length=30, required=False, help_text="optional", widget=forms.PasswordInput)

    image_share = forms.BooleanField(
        label="image_share", required=False, widget=forms.CheckboxInput)

    post_share = forms.BooleanField(
        label="post_share", required=False, widget=forms.CheckboxInput)

    append_slash = forms.BooleanField(
        label="append_slash", required=False, widget=forms.CheckboxInput)

    class Meta:
        model = Node
        fields = ['foreign_server_hostname', 'foreign_server_username', 'foreign_server_password',  'foreign_server_api_location', 'username_registered_on_foreign_server',
                  'password_registered_on_foreign_server', 'image_share', 'post_share', 'append_slash']
