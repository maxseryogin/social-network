from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='main'),
    path('login/', auth_views.LoginView.as_view(template_name='messenger/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('chats/', views.chat_list, name='chat_list'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('search/', views.user_search, name='user_search'),
    path('chat/<int:chat_id>/send/', views.send_message, name='send_message'),
    path('chat/create/<int:user_id>/', views.create_chat, name='create_chat'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<int:user_id>/', views.profile_view, name='profile_view'),
    path('message/<int:message_id>/edit/', views.edit_message, name='edit_message'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('get_user_status/<int:user_id>/', views.get_user_status, name='get_user_status'),
    path('chat/<int:chat_id>/messages/', views.get_messages, name='get_messages'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
