from django.urls import path
from . import views
urlpatterns = [
   path('', views.retrieve_all_public_posts_on_local_server),
    path('<str:post_id>/', views.retrieve_single_post_with_id),
    path('<str:post_id>/comments/',  views.comments_retrieval_and_creation_to_post_id),
]