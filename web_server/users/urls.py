from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    path('signup/', views.register, name='register'),
    path('profile/<path:user_id>/', views.profile, name='profile'),
    path('mandala/', views.mandala, name='mandala'),
    path('login/', views.CustomLogin.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('addfriend/', views.add_friend, name='add_friend'),

    path('view_post/<path:post_path>/comments/', views.view_post_comment, name='view_post_comment'),
    path('view_post/<path:post_path>/', views.view_post, name='view_post')
]
