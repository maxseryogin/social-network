from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='messenger/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('chats/', views.chat_list, name='chat_list'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('search/', views.user_search, name='user_search'),
    path('chat/<int:chat_id>/send/', views.send_message, name='send_message'),
    path('chat/create/<int:user_id>/', views.create_chat, name='create_chat'),
]
