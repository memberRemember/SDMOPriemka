from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from ..forms import *
from ..models import *


#####################################    ОНЛАЙН ЧАТ  НАЧАЛО  #######################################
@login_required
def start_chat(request):
    secretary = User.objects.filter(role=1).first() # щас берется первый попавшийся секретарь. да криво
    
    if not secretary:
        return JsonResponse({'status': 'error', 'message': 'Секретарь не найден'}, status=404)
    
    chat, created = Chat.objects.get_or_create(
        user=request.user,
        secretary=secretary,
        is_active=True
    )
    
    return JsonResponse({
        'status': 'success',
        'chat_id': chat.id,
        'secretary_name': secretary.get_full_name()
    })

@login_required
def send_message(request):
    chat_id = request.POST.get('chat_id')
    text = request.POST.get('text')
    
    try:
        chat = Chat.objects.get(id=chat_id)
        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            text=text
        )
        
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'text': message.text,
                'sender_id': request.user.id,
                'is_read': False,
                'timestamp': message.timestamp.strftime("%H:%M %d.%m.%Y")
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def get_messages(request):
    chat_id = request.GET.get('chat_id')
    last_id = int(request.GET.get('last_id', 0))
    
    try:
        chat = Chat.objects.get(id=chat_id)
        
        if not chat.is_active:
            return JsonResponse({
                'status': 'error',
                'message': 'Чат закрыт'
            }, status=400)
            
        messages = Message.objects.filter(
            chat=chat,
            id__gt=last_id
        ).order_by('timestamp')
        
        return JsonResponse({
            'status': 'success',
            'messages': [{
                'id': msg.id,
                'text': msg.text,
                'sender_id': msg.sender.id,
                'is_read': msg.is_read,
                'timestamp': msg.timestamp.strftime("%H:%M %d.%m.%Y")
            } for msg in messages]
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
# Чтение сообщений секретаря со стороны пользователя
@login_required
def mark_secretary_messages_read(request):
    if request.method == 'POST':
        chat_id = request.POST.get('chat_id')
        try:
            chat = Chat.objects.get(id=chat_id)
            updated = Message.objects.filter(
                chat=chat,
                sender=chat.secretary,
                is_read=False
            ).update(is_read=True)
            print(f"Updated {updated} secretary messages as read for chat {chat_id}")
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'}, status=400)

# Чтение сообщений пользователя со стороны секретаря
@login_required
def mark_user_messages_read(request, chat_id):
    if request.method == 'POST':
        chat = get_object_or_404(Chat, id=chat_id, secretary=request.user)
        
        Message.objects.filter(
            chat=chat,
            sender=chat.user,
            is_read=False
        ).update(is_read=True)
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'}, status=400)


@login_required
def priemka_lc_chats(request):
    if not request.user.role or request.user.role.id not in [1, 2, 3]:
        return redirect('priemka_index_page')
    
    context = {}
    user_info = {}
    
    if request.user.is_authenticated:
        user_info = {
            'short_name': request.user.get_short_name(),
            'full_name': request.user.get_full_name()
        }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        filter_type = request.GET.get('filter', 'active')
        
        if request.user.role.id == 1:  # Секретарь
            queryset = Chat.objects.filter(secretary=request.user)
        elif request.user.role.id == 2:  # Админ
            queryset = Chat.objects.all()
        else:  # Другие роли (например, id=3), если нужно
            return JsonResponse({'active_chats': []}, status=403)

        if filter_type == 'active':
            queryset = queryset.filter(is_active=True)
        else:
            queryset = queryset.filter(is_active=False)

        chats_data = [
            {
                'id': chat.id,
                'created_at': chat.created_at.strftime('%H:%M %d.%m.%y'),
                'is_active': chat.is_active,
                'secretary': chat.secretary.get_full_name(),
                'user': chat.user.get_full_name(),
                'unread_count': Message.objects.filter(
                    chat=chat,
                    sender=chat.user,
                    is_read=False
                ).count()
            }
            for chat in queryset
        ]
        
        return JsonResponse({'active_chats': chats_data})
    
    if request.user.role.id == 1:  # Секретарь
        active_chats = Chat.objects.filter(
            secretary=request.user,
            is_active=True
        ).select_related('user').prefetch_related('messages')
    elif request.user.role.id == 2:  # Админ
        active_chats = Chat.objects.filter(
            is_active=True
        ).select_related('user').prefetch_related('messages')
    else:
        active_chats = Chat.objects.none()

    for chat in active_chats:
        chat.unread_count = Message.objects.filter(
            chat=chat,
            sender=chat.user,
            is_read=False
        ).count()
    
    users = User.objects.all()
    context['users'] = users
    context['active_chats'] = active_chats
    context['filter_type'] = 'active'
    context['active_page'] = 'chats'
    context['user_info'] = user_info

    return render(request, 'priemka/priemka_lc_chats.html', context)


@login_required
def chat_detail(request, chat_id):
    if not request.user.role or request.user.role.id not in [1, 2]:
        return redirect('priemka_index_page')
    
    user_info = {
        'short_name': request.user.get_short_name(),
        'full_name': request.user.get_full_name()
    } if request.user.is_authenticated else None


    if request.user.role.id == 1:  # Секретарь
        chat = get_object_or_404(Chat, id=chat_id, secretary=request.user)
    elif request.user.role.id == 2:  # Админ
        chat = get_object_or_404(Chat, id=chat_id)
    else:
        return redirect('priemka_index_page')

    messages = Message.objects.filter(chat=chat).order_by('timestamp')
    
    return render(request, 'priemka/priemka_lc_chats_details.html', {
        'chat': chat,
        'messages': messages,
        'active_page': 'secretary_chat',
        'user_info': user_info,
    })

@login_required
def send_chat_message(request, chat_id):
    if request.method == 'POST':
        chat = get_object_or_404(Chat, id=chat_id, secretary=request.user)
        
        if not chat.is_active:
            return JsonResponse({'status': 'error', 'message': 'Чат закрыт'}, status=400)
        
        message_text = request.POST.get('message', '').strip()
        if not message_text:
            return JsonResponse({'status': 'error', 'message': 'Сообщение не может быть пустым'}, status=400)
        
        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            text=message_text
        )
        
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'text': message.text,
                'timestamp': message.timestamp.strftime("%H:%M %d.%m.%Y")
            }
        })
    
    return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'}, status=400)

@login_required
def get_chat_messages(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, secretary=request.user)
    last_id = request.GET.get('last_id', None)
    
    messages = Message.objects.filter(chat=chat).order_by('timestamp')
    if last_id:
        try:
            last_id = int(last_id)
            messages = messages.filter(id__gt=last_id)
        except ValueError:
            pass
    
    return JsonResponse({
        'status': 'success',
        'messages': [{
            'id': msg.id,
            'text': msg.text,
            'time': msg.timestamp.strftime("%H:%M"),
            'is_read': msg.is_read,
            'sender_id': msg.sender.id,
            'is_me': msg.sender == request.user
        } for msg in messages]
    })


@login_required
def close_chat(request, chat_id):
    if request.method == 'POST':
        chat = get_object_or_404(Chat, id=chat_id, secretary=request.user)
        
        if chat.is_active:
            chat.is_active = False
            chat.closed_at = timezone.now()
            chat.save()
            
            return JsonResponse({
                'status': 'success',
                'chat_id': chat.id,
                'is_active': chat.is_active,
                'closed_at': chat.closed_at.strftime("%H:%M %d.%m.%Y")
            })
        
        return JsonResponse({'status': 'error', 'message': 'Чат уже закрыт'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'}, status=400)

@login_required
def reopen_chat(request, chat_id):
    if request.method == 'POST':
        chat = get_object_or_404(Chat, id=chat_id, secretary=request.user)
        
        if not chat.is_active:
            chat.is_active = True
            chat.closed_at = None
            chat.save()
            
            return JsonResponse({'status': 'success'})
        
        return JsonResponse({'status': 'error', 'message': 'Чат уже активен'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'}, status=400)
    
################    ОНЛАЙН ЧАТ  КОНЕЦ  ################