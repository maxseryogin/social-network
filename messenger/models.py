from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.username
    

class Chat(models.Model):
    users = models.ManyToManyField(User, related_name='chats')
    messages = models.ManyToManyField('Message', related_name='chats')

    def __str__(self):
        return f"Chat between {self.users.first().username} and {self.users.last().username}"
    
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='message_attachments/', null=True, blank=True)
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    description = models.TextField(max_length=500, blank=True)
    name = models.CharField(max_length=100, blank=True, default='')
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    def is_online(self):
        if not self.last_activity:
            return False
        now = timezone.now()
        return (now - self.last_activity) < timedelta(minutes=5)

    def get_last_seen(self):
        if not self.last_activity:
            return 'Никогда не был в сети'
            
        now = timezone.now()
        diff = now - self.last_activity

        if (now - self.last_activity) < timedelta(minutes=5):
            return 'В сети'
            
        if diff.days > 0:
            return f'Был в сети {diff.days} дней назад'
        elif diff.seconds // 3600 > 0:
            hours = diff.seconds // 3600
            return f'Был в сети {hours} часов назад'
        elif diff.seconds // 60 > 0:
            minutes = diff.seconds // 60
            return f'Был в сети {minutes} минут назад'
        else:
            return 'Только что'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

