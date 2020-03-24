from django.contrib import admin
from nodes.models import Node
from .forms import ForeignServerRegisterForm


class NodeAdmin(admin.ModelAdmin):
    list_display = ['foreign_server_hostname']

    form = ForeignServerRegisterForm
    # fields that will be displayed on Register Form
    add_fieldsets = (
        (None, {
            'fields': ('foreign_server_hostname', 'foreign_server_username', 'foreign_server_password', 'foreign_server_api_location',  'hostname_registered_on_foreign_server', 'password_registered_on_foreign_server', 'image_share', 'post_share', 'append_slash'),
            'classes': ('extrapretty',)
        }),

    )

    # set foreign_server_hostname, foreign_server_passwordas readonly in ChangeForm
    # set nothing readonly in UserRegistration Form

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['foreign_server_hostname', 'foreign_server_api_location', 'foreign_server_username', 'foreign_server_password']
        else:
            return []

    model = Node


# Register your models here.
admin.site.register(Node, NodeAdmin)
