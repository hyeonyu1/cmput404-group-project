from django.urls import path
from . import views
urlpatterns = [
    path('', views.send_friend_request,
         name="send_friend_request"),
    path('handle', views.handle_friend_request,
         name="handle_friend_request"),
    path('<str:author_id>', views.retrieve_friend_request_of_author_id,
         name="retrieve_friend_request_of_author_id")


]
