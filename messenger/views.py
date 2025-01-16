from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Chat, Message, User
from django.db.models import Q
from .forms import SimpleRegisterForm
from django.contrib.auth import logout

def index(request):
    """Главная страница"""
    return render(request, 'messenger/index.html')

@login_required
def chat_list(request):
    """Список всех чатов пользователя"""
    chats = Chat.objects.filter(users=request.user)
    return render(request, 'messenger/chat_list.html', {'chats': chats})

@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, users=request.user)
    messages = chat.messages.all().order_by('timestamp')
    return render(request, 'messenger/chat_detail.html', {
        'chat': chat,
        'messages': messages
    })

@login_required
def send_message(request, chat_id):
    """Отправка сообщения"""
    if request.method == 'POST':
        chat = get_object_or_404(Chat, id=chat_id, users=request.user)
        content = request.POST.get('content')
        if content:
            message = Message.objects.create(
                sender=request.user,
                content=content
            )
            chat.messages.add(message)
            return redirect('chat_detail', chat_id=chat_id)
    return redirect('chat_detail', chat_id=chat_id)

@login_required
def create_chat(request, user_id):
    """Создание нового чата с пользователем"""
    other_user = get_object_or_404(User, id=user_id)
    
    # Проверяем, существует ли уже чат между пользователями
    existing_chat = Chat.objects.filter(users=request.user).filter(users=other_user).first()
    
    if existing_chat:
        return redirect('chat_detail', chat_id=existing_chat.id)
    
    # Создаем новый чат
    chat = Chat.objects.create()
    chat.users.add(request.user, other_user)
    
    return redirect('chat_detail', chat_id=chat.id)

@login_required
def user_search(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(
        Q(username__icontains=query) | Q(name__icontains=query)
    ).exclude(id=request.user.id)
    return render(request, 'messenger/user_search.html', {'users': users})

def register(request):
    if request.method == "POST":
        form = SimpleRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SimpleRegisterForm()
    return render(request, 'registration/register.html', {"form": form})

def logout_view(request):
    logout(request)
    return redirect('index')
