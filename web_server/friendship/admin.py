from django.contrib import admin

# Register your models here.
from .models import Friend, FriendRequest
admin.site.register(Friend)
admin.site.register(FriendRequest)
