from django.urls import path
from . import views
urlpatterns = [
    path('', views.retrieve_all_public_posts_on_local_server, name='post_index'),
    path('', views.retrieve_all_public_posts_on_local_server, name='stream'),
    path('<str:post_id>/', views.retrieve_single_post_with_id, name='post'),
    path('<str:post_id>/comments/',  views.comments_retrieval_and_creation_to_post_id, name="get_or_add_comment"),
]