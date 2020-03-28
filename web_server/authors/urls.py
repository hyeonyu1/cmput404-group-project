from django.urls import path
from . import views
urlpatterns = [
    # API URLS
    path('posts/', views.post_creation_and_retrieval_to_curr_auth_user,
         name="add_or_get_post"),
    path('posts/', views.post_creation_and_retrieval_to_curr_auth_user,
         name="stream"),
    # GET is also the user UI for editing
    path('posts/<str:post_id>', views.post_edit_and_delete,
         name="edit_or_delete_post"),
    path('<str:author_id>/posts/', views.retrieve_posts_of_author_id_visible_to_current_auth_user,
         name="retrieve_posts_of_author_id_visible_to_current_auth_user"),
    path('<path:author_id>/friends/', views.friend_checking_and_retrieval_of_author_id,
         name="friend_checking_and_retrieval_of_author_id"),
    path('<str:author1_id>/friends/<path:author2_id>/',
         views.check_if_two_authors_are_friends, name="check_if_two_authors_are_friends"),
    path('<str:author_id>/', views.retrieve_author_profile,
         name="retrieve_author_profile"),
    path('<str:author_id>/update', views.update_author_profile,
         name="update_author_profile"),
    path('unfriend', views.unfriend, name="unfriend"),
    path('<str:author_id>/addfriend/', views.view_list_of_available_authors_to_befriend,
         name="view_list_of_available_authors_to_befriend"),

    # Internal Use API's
    path('', views.get_all_authors, name='all_authors'),

    # Webpage URLS
    path('create_post', views.post_creation_page, name='post_create_form'),
]
