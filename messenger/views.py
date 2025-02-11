from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Chat, Message, User, Profile
from django.db.models import Q
from .forms import SimpleRegisterForm, UserProfileForm
from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
import json
from django.template.loader import render_to_string

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

        if content or attachment:
            message = Message.objects.create(
                sender=request.user,
                content=content
            )
            
            if attachment:
                message.attachment = attachment
                message.save()
                
            chat.messages.add(message)
            return redirect('chat_detail', chat_id=chat_id)
    return redirect('chat_detail', chat_id=chat_id)

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
        Q(username__icontains=query) | Q(name__icontains=query)
    ).exclude(id=request.user.id).select_related('profile')
    return render(request, 'messenger/user_search.html', {'users': users})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

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
            return redirect('index')
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
    try:
        user = User.objects.get(id=user_id)
        status = user.profile.get_last_seen()
        return JsonResponse({'status': status})
    except User.DoesNotExist:
        return JsonResponse({'status': 'Пользователь не найден'}, status=404)

@login_required
def get_messages(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, users=request.user)
    messages = Message.objects.filter(chats=chat).order_by('-timestamp')
    
    messages_html = render_to_string('messenger/messages_partial.html', {
        'messages': messages,
        'request': request
    })
    
    return JsonResponse({'messages_html': messages_html})
