from django.urls import path
from . import views
urlpatterns = [
    path('<str:comment_id>/', views.delete_single_comment, name="delete_comment"),
]