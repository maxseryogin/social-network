from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Chat, Message

admin.site.register(User, UserAdmin)
admin.site.register(Chat)
admin.site.register(Message)