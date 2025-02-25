from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Chat, Message, User, Profile
from django.db.models import Q
from .forms import CustomUserCreationForm, UserProfileForm
from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
import json
from django.template.loader import render_to_string
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.urls import reverse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie

def index(request):
    return render(request, 'messenger/index.html')

@login_required
def chat_list(request):
    chats = Chat.objects.filter(users=request.user)
    return render(request, 'messenger/chat_list.html', {'chats': chats})

@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, users=request.user)
    messages = Message.objects.filter(chats=chat).order_by('-timestamp')
    return render(request, 'messenger/chat_detail.html', {
        'chat': chat,
        'messages': messages
    })

@login_required
def send_message(request, chat_id):
    if request.method == 'POST':
        chat = get_object_or_404(Chat, id=chat_id, users=request.user)
        content = request.POST.get('content')
        attachment = request.FILES.get('attachment')
        reply_to_id = request.POST.get('reply_to')

        if content or attachment:
            message = Message.objects.create(
                sender=request.user,
                content=content
            )
            
            if attachment:
                message.attachment = attachment
                
            if reply_to_id:
                try:
                    reply_to_message = Message.objects.get(id=reply_to_id)
                    message.reply_to = reply_to_message
                except Message.DoesNotExist:
                    pass
                
            message.save()
            chat.messages.add(message)

            # Отправляем уведомление всем пользователям чата, кроме отправителя
            channel_layer = get_channel_layer()
            for user in chat.users.exclude(id=request.user.id):
                async_to_sync(channel_layer.group_send)(
                    f"user_{user.id}",
                    {
                        "type": "notification",
                        "sender_name": request.user.username,
                        "sender_avatar": request.user.profile.avatar.url if request.user.profile.avatar else None,
                        "message": content[:50] + "..." if len(content) > 50 else content,
                        "chat_id": chat_id
                    }
                )
            
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def create_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    existing_chat = Chat.objects.filter(users=request.user).filter(users=other_user).first()
    
    if existing_chat:
        return redirect('chat_detail', chat_id=existing_chat.id)
    
    chat = Chat.objects.create()
    chat.users.add(request.user, other_user)
    
    return redirect('chat_detail', chat_id=chat.id)

@login_required
def user_search(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(
        Q(username__icontains=query) | 
        Q(profile__name__icontains=query)  # Ищем по имени в профиле
    ).exclude(id=request.user.id).select_related('profile').distinct()
    return render(request, 'messenger/user_search.html', {'users': users})

@ensure_csrf_cookie  # This ensures the CSRF cookie is always set
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # If it's an AJAX request, return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'redirect': '/'})
            return redirect('index')
        else:
            # If it's an AJAX request, return form errors
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        form = CustomUserCreationForm()
    
    # Get and print CSRF token for debugging
    csrf_token = get_token(request)
    print("Current CSRF Token:", csrf_token)
    
    return render(request, 'registration/register.html', {
        'form': form,
        'csrf_token': csrf_token
    })

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('main')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'messenger/profile_edit.html', {'form': form})

@login_required
def profile_view(request, user_id):
    user = get_object_or_404(User.objects.select_related('profile'), id=user_id)
    profile = user.profile
    return render(request, 'messenger/profile_view.html', {
        'profile_user': user,
        'profile': profile
    })

@login_required
@require_POST
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.sender != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    message.delete()
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.sender != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    data = json.loads(request.body)
    new_content = data.get('content')
    
    if not new_content:
        return JsonResponse({'error': 'Content is required'}, status=400)
    
    message.content = new_content
    message.save()
    
    return JsonResponse({'status': 'success'})

@login_required
def get_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    is_online = user.profile.is_online()
    status = "В сети" if is_online else user.profile.get_last_seen()
    
    return JsonResponse({
        'status': status,
        'is_online': is_online
    })

@login_required
def get_messages(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, users=request.user)
    messages = Message.objects.filter(chats=chat).order_by('-timestamp')
    
    messages_html = render_to_string('messenger/messages_partial.html', {
        'messages': messages,
        'request': request
    })
    
    return JsonResponse({'messages_html': messages_html})

def main_view(request):
    return render(request, 'messenger/index.html')
