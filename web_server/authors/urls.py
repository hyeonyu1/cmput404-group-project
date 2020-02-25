from django.urls import path
from . import views
urlpatterns = [
   path('posts/', views.post_creation_and_retrival_to_curr_auth_user),
   path('posts/createPost', views.post_creation_page),
    path('<str:author_id>/posts/', views.retrieve_posts_of_author_id_visible_to_current_auth_user),
    path('<str:author_id>/friends/', views.friend_checking_and_retrieval_of_author_id),
    path('<str:author1_id>/friends/<str:author2_id>/', views.check_if_two_authors_are_friends),
    path('<str:author_id>/', views.retrieve_author_profile)
]