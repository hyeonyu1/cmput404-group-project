from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import UserRegisterForm, UserChangeForm
from .models import Author


class CustomUserAdmin(UserAdmin):
    add_form = UserRegisterForm
    form = UserChangeForm
    # fields that will be displayed on UserRegistration Form
    add_fieldsets = (
        ('Personal Information', {
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'display_name', 'bio', 'github')
        }),

    )
    # fields that will be displayed on ChangeForm
    fieldsets = (
        ('Personal Information', {
            'fields': ('username', 'password', 'uid', 'id', 'email', 'first_name', 'last_name', 'display_name', 'bio', 'github')
        }),
        ('Permission', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),

    )
    model = Author

    list_display = ['username', 'email']

    # set username, uid, id as readonly in ChangeForm
    # set nothing readonly in UserRegistration Form
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['username', 'uid', 'id']
        else:
            return []

    def save_model(self, request, obj, form, change):
        # if it's creating new model instance
        if not change:
            obj.is_active = False
            host = request.get_host()

            url = host + "/author/" + str(obj.id.hex)
            obj.url = url
            obj.uid = url
            obj.host = host

        return super(CustomUserAdmin, self).save_model(request, obj, form, change)


admin.site.register(Author, CustomUserAdmin)
