from django.utils import timezone
from django.contrib.auth.models import User
from .models import Profile

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Проверяем, что запрос не является AJAX-запросом проверки статуса
            if not request.path.startswith('/get_user_status/'):
                profile, created = Profile.objects.get_or_create(user=request.user)
                profile.last_activity = timezone.now()
                profile.save()
        
        response = self.get_response(request)
        return response 