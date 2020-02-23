from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import UserRegisterForm, UserChangeForm
from .models import Author


class CustomUserAdmin(UserAdmin):
    add_form = UserRegisterForm
    form = UserChangeForm
    model = Author
    list_display = ['email', 'username']


admin.site.register(Author, CustomUserAdmin)
