from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from ..forms import *
from ..email_notifications import *
from ..models import *


from ..models import *


def priemka_lc_appointments(request):
    context = {
        'active_page': 'appointments',
    }

    if not request.user.is_authenticated:
        raise Http404("Страница не найдена")

    context['user_info'] = {
        'short_name': request.user.get_short_name(),
        'full_name': request.user.get_full_name()
    }

    deputies = Deputy.objects.filter(appointment__user=request.user).distinct()

    # AJAX-запрос (фильтрация записей)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        filter_type = request.GET.get('filter', 'actual')
        status_filter = request.GET.get('status', 'all')
        deputy_filter = request.GET.get('deputy', 'all')
        search_id = request.GET.get('search_id', '')

        queryset = Appointment.objects.filter(user=request.user)

        if filter_type == 'archived':
            queryset = queryset.filter(is_archived=True)
        else:
            queryset = queryset.filter(is_archived=False)

        if status_filter != 'all':
            queryset = queryset.filter(appointment_status__id=int(status_filter))

        if deputy_filter != 'all':
            queryset = queryset.filter(deputy=int(deputy_filter))

        if search_id:
            queryset = queryset.filter(id__startswith=search_id)

        appointments_data = [
            {
                'id': appointment.id,
                'deputy': f"{appointment.deputy.last_name} {appointment.deputy.first_name} {appointment.deputy.patronymic_name}",
                'position': appointment.deputy.position,
                'theme': str(appointment.appointment_theme),
                'title': appointment.title,
                'appointed_date': appointment.appointed_date.strftime('%d.%m.%Y'),
                'appointed_time': appointment.appointed_time.strftime('%H:%M'),
                'creation_date': appointment.creation_date.strftime('%H:%M %d.%m.%y'),
                'status_id': appointment.appointment_status.id,
                'status_name': str(appointment.appointment_status),
            }
            for appointment in queryset
        ]

        return JsonResponse({'appointments': appointments_data})

    # Обычный GET-запрос (рендеринг страницы)
    appointments = Appointment.objects.filter(user=request.user, is_archived=False)
    
    context['deputies'] = deputies
    context['appointments'] = appointments
    context['filter_type'] = 'actual'

    return render(request, 'priemka/priemka_lc_appointments.html', context)

def priemka_lc_appointments_manage(request):
    context = {
        'active_page':'appointments_manage',
    }
    
    if not request.user.is_authenticated:
        raise Http404("Страница не найдена")
    
    if request.user.is_authenticated:
        context['user_info'] = {
            'short_name': request.user.get_short_name(),
            'full_name': request.user.get_full_name()
        }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        filter_type = request.GET.get('filter', 'actual')
        status_filter = request.GET.get('status', 'all')
        user_filter = request.GET.get('user', 'all')
        search_id = request.GET.get('search_id', '')

        queryset = Appointment.objects.all().select_related('user', 'deputy', 'appointment_status')

        if filter_type == 'archived':
            queryset = queryset.filter(is_archived=True)
        else:
            queryset = queryset.filter(is_archived=False)
        
        if status_filter != 'all':
            queryset = queryset.filter(appointment_status__id=int(status_filter))

        if user_filter != 'all':
            queryset = queryset.filter(user__id=int(user_filter))

        if search_id:
            queryset = queryset.filter(id__startswith=search_id)
        
        appointments_data = [
            {
                'id': appointment.id,
                'user': f"{appointment.user.last_name} {appointment.user.first_name} {appointment.user.patronymic_name}",
                'deputy': f"{appointment.deputy.last_name} {appointment.deputy.first_name} {appointment.deputy.patronymic_name}",
                'position': appointment.deputy.position,
                'theme': str(appointment.appointment_theme),
                'title': appointment.title,
                'appointed_date': appointment.appointed_date.strftime('%d.%m.%Y'),
                'appointed_time': appointment.appointed_time.strftime('%H:%M'),
                'creation_date': appointment.creation_date.strftime('%H:%M %d.%m.%y'),
                'status_id': appointment.appointment_status.id,
                'status_name': str(appointment.appointment_status),
            }
            for appointment in queryset
        ]
        
        return JsonResponse({'appointments': appointments_data})
    
    
    appointments = Appointment.objects.all().filter(is_archived=False)
    deputies = Deputy.objects.all()
    users = User.objects.filter(appointment__isnull=False).distinct()

    context['deputies'] = deputies
    context['appointments'] = appointments
    context['filter_type'] = 'actual'
    context['users'] = users
    # context['active_page'] = "appointments",
    
    return render(request, 'priemka/priemka_lc_appointments_manage.html', context)


@login_required
def priemka_lc_appointments_today_deputy(request):
    
    context = {
        'active_page': 'appointments_today_deputy',
    }
    
    if not request.user.is_authenticated:
        raise Http404("Страница не найдена")
    
    if request.user.is_authenticated:
        context['user_info'] = {
            'short_name': request.user.get_short_name(),
            'full_name': request.user.get_full_name()
        }
    

    try:
        deputy = Deputy.objects.get(user=request.user)
    except Deputy.DoesNotExist:
        deputy = None
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        filter_type = request.GET.get('filter', 'actual')
        status_filter = request.GET.get('status', '2') 
        user_filter = request.GET.get('user', 'all')


        queryset = Appointment.objects.filter(
            deputy=deputy, 
            appointment_status__id=2, 
            appointed_date=datetime.today().strftime('%Y-%d-%m'), 
            is_archived=False
        ).order_by('appointed_time') if deputy else Appointment.objects.none()

        if user_filter != 'all':
            queryset = queryset.filter(user__id=int(user_filter))
        
        appointments_data = [
            {
                'id': appointment.id,
                'user': f"{appointment.user.last_name} {appointment.user.first_name} {appointment.user.patronymic_name}",
                'deputy': f"{appointment.deputy.last_name} {appointment.deputy.first_name} {appointment.deputy.patronymic_name}",
                'position': appointment.deputy.position,
                'theme': str(appointment.appointment_theme),
                'title': appointment.title,
                'appointed_date': appointment.appointed_date.strftime('%d.%m.%Y'),
                'appointed_time': appointment.appointed_time.strftime('%H:%M'),
                'creation_date': appointment.creation_date.strftime('%H:%M %d.%m.%y'),
                'status_id': appointment.appointment_status.id,
                'status_name': str(appointment.appointment_status),
            }
            for appointment in queryset
        ]

        
        return JsonResponse({'appointments': appointments_data})
    
    appointments = Appointment.objects.filter(
        deputy=deputy,
        is_archived=False,
        appointment_status__id=2,
        appointed_date=datetime.today().strftime('%Y-%m-%d')
    ).order_by('appointed_time') if deputy else Appointment.objects.none()

    
    deputies = Deputy.objects.all()
    users = User.objects.filter(appointment__isnull=False, appointment__appointed_date=datetime.today().strftime('%Y-%m-%d')).distinct()

    context['deputies'] = deputies
    context['appointments'] = appointments
    context['filter_type'] = 'registered'
    context['users'] = users

    return render(request, 'priemka/priemka_lc_appointments_today_deputy.html', context)

@login_required
def priemka_lc_appointments_deputy(request):
    
    context = {
        'active_page': 'appointments_deputy',
    }
    
    if not request.user.is_authenticated:
        raise Http404("Страница не найдена")
    
    if request.user.is_authenticated:
        context['user_info'] = {
            'short_name': request.user.get_short_name(),
            'full_name': request.user.get_full_name()
        }
    

    try:
        deputy = Deputy.objects.get(user=request.user)
    except Deputy.DoesNotExist:
        deputy = None
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        filter_type = request.GET.get('filter', 'registered')
        status_filter = request.GET.get('status', 'all') 
        user_filter = request.GET.get('user', 'all')
        search_id = request.GET.get('search_id', '')


        queryset = Appointment.objects.filter(deputy=deputy) if deputy else Appointment.objects.none()

        if filter_type == 'archived':
            queryset = queryset.filter(is_archived=True)
        elif filter_type == 'registered':
            queryset = queryset.filter(appointment_status=2, is_archived=False)
        else:
            queryset = queryset.filter(is_archived=False)
        
        if status_filter != 'all':
            queryset = queryset.filter(appointment_status__id=int(status_filter))

        if user_filter != 'all':
            queryset = queryset.filter(user__id=int(user_filter))

        if search_id:
            queryset = queryset.filter(id__startswith=search_id)
        
        appointments_data = [
            {
                'id': appointment.id,
                'user': f"{appointment.user.last_name} {appointment.user.first_name} {appointment.user.patronymic_name}",
                'deputy': f"{appointment.deputy.last_name} {appointment.deputy.first_name} {appointment.deputy.patronymic_name}",
                'position': appointment.deputy.position,
                'theme': str(appointment.appointment_theme),
                'title': appointment.title,
                'appointed_date': appointment.appointed_date.strftime('%d.%m.%Y'),
                'appointed_time': appointment.appointed_time.strftime('%H:%M'),
                'creation_date': appointment.creation_date.strftime('%H:%M %d.%m.%y'),
                'status_id': appointment.appointment_status.id,
                'status_name': str(appointment.appointment_status),
            }
            for appointment in queryset
        ]
        
        return JsonResponse({'appointments': appointments_data})
    
    appointments = Appointment.objects.filter(
        deputy=deputy,
        is_archived=False,
        appointment_status__id=2
    ) if deputy else Appointment.objects.none()
    
    users = User.objects.filter(appointment__isnull=False, appointment__deputy=deputy).distinct()

    context['appointments'] = appointments
    context['filter_type'] = 'registered'
    context['users'] = users

    return render(request, 'priemka/priemka_lc_appointments_deputy.html', context)

@login_required
def create_appointment(request, deputy_id):
    deputy = get_object_or_404(Deputy, pk=deputy_id)

    if request.user.is_authenticated:
        user_info = {
            'short_name': request.user.get_short_name(),
            'full_name': request.user.get_full_name()
        }
        user_role = request.user.role.id
        print(user_role)
    else:
        user_role = None

    if request.method == 'POST':
        form = AppointmentForm(request.POST, deputy=deputy, user_role=user_role)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.deputy = deputy
            appointment.user = form.cleaned_data.get('user', request.user)
            appointment.save()
            
            send_appointment_notification(
                user=appointment.user,
                appointment=appointment,
                deputy=deputy
            )
            
            return redirect('appointment_success')
    else:
        form = AppointmentForm(deputy=deputy, user_role=user_role)
    
    themes = AppointmentTheme.objects.all()
    return render(request, 'priemka/appointment_creation.html', {
        'deputy': deputy,
        'form': form,
        'themes': themes,
        'user_info': user_info,
        'user_role': user_role,
    })

def get_time_slots(request, deputy_id):
    deputy = get_object_or_404(Deputy, pk=deputy_id)
    selected_date = request.GET.get('date')
    
    form = AppointmentForm(deputy=deputy)
    time_slots = form.get_available_time_slots(selected_date)
    
    return JsonResponse({'time_slots': time_slots})


#################################### рефакторинг страница детали записи ###########################################
@login_required
def appointment_details(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    user_info = get_user_info(request.user) if request.user.is_authenticated else None
    can_move = can_move_appointment(appointment)

    if request.method == 'POST':
        return handle_post_request(request, appointment, user_info, can_move)
    
    return render_appointment_get_request(request, appointment, user_info, can_move)

def get_user_info(user):

    return {
        'short_name': user.get_short_name(),
        'full_name': user.get_full_name()
    }

def can_move_appointment(appointment):
    current_time = timezone.now()
    appointment_datetime = timezone.make_aware(
        datetime.combine(appointment.appointed_date, appointment.appointed_time)
    )
    return current_time < (appointment_datetime - timedelta(hours=1))

def handle_post_request(request, appointment, user_info, can_move):
    actions = {
        'move_appointment': handle_move_appointment,
        'register_appointment': handle_register_appointment,
        'finish_appointment': handle_finish_appointment,
        'cancel_appointment': handle_cancel_appointment,
        'decline_appointment': handle_decline_appointment,
    }

    for action, handler in actions.items():
        if action in request.POST:
            return handler(request, appointment, user_info, can_move)
    
    return render(request, 'priemka/appointment_details.html', get_appointment_context(appointment, user_info, error="Неизвестное действие"))

def handle_move_appointment(request, appointment, user_info, can_move):
    print("POST MOVE")
    if not can_move:
        print("NOT CAN MOVE")
        return render(request, 'priemka/appointment_details.html', get_appointment_context(
            appointment, user_info, error="Нельзя перенести запись менее чем за час до её начала."
        ))

    form = MoveAppointmentForm(request.POST, deputy=appointment.deputy, instance=appointment)
    if form.is_valid():
        print("VALID VALID VALID")
        update_appointment(appointment, form.cleaned_data, status_id=1, request_user=request.user)
        
        if any(field in form.changed_data for field in ['appointed_date', 'appointed_time']):
            send_appointment_moved_notification(
                user=appointment.user,
                appointment=appointment,
                changed_by=request.user,
                update_reason=appointment.last_update_reason
            )
        
        print(f"Saved: {appointment.appointed_date}, {appointment.appointed_time}, {appointment.appointment_status}")
        return redirect('priemka_appointment_details_page', appointment_id=appointment.id)
    
    print("FORM INVALID:", form.errors)
    return render(request, 'priemka/appointment_details.html', get_appointment_context(appointment, user_info, form=form))

def handle_register_appointment(request, appointment, user_info, can_move):
    print("POST REGISTER")
    update_appointment(appointment, {'update_reason': request.POST.get('update_reason', '')}, status_id=2, request_user=request.user)
    print(f"Registered: {appointment.appointment_status}")
    return redirect('priemka_appointment_details_page', appointment_id=appointment.id)

def handle_finish_appointment(request, appointment, user_info, can_move):
    """Завершение"""
    print("POST FINISH")
    update_appointment(appointment, {'update_reason': request.POST.get('update_reason', ''), 'is_archived': True}, status_id=3, request_user=request.user)
    print(f"Finished: {appointment.appointment_status}, Archived: {appointment.is_archived}")
    return redirect('priemka_appointment_details_page', appointment_id=appointment.id)

def handle_cancel_appointment(request, appointment, user_info, can_move):
    print("POST CANCEL")
    update_appointment(appointment, {'update_reason': request.POST.get('update_reason', ''), 'is_archived': True}, status_id=4, request_user=request.user)
    print(f"Canceled: {appointment.appointment_status}, Archived: {appointment.is_archived}")
    return redirect('priemka_appointment_details_page', appointment_id=appointment.id)

def handle_decline_appointment(request, appointment, user_info, can_move):
    print("POST DECLINE")
    update_appointment(appointment, {'update_reason': request.POST.get('update_reason', ''), 'is_archived': True}, status_id=5, request_user=request.user)
    print(f"Declined: {appointment.appointment_status}, Archived: {appointment.is_archived}")
    return redirect('priemka_appointment_details_page', appointment_id=appointment.id)

def update_appointment(appointment, data, status_id, request_user):
    appointment.appointment_status = AppointmentStatus.objects.get(id=status_id)
    appointment.last_updated_by = request_user
    appointment.last_update_reason = data.get('update_reason', '')

    if 'appointed_date' in data:
        appointment.appointed_date = data['appointed_date']
    if 'appointed_time' in data:
        appointment.appointed_time = data['appointed_time']
    if 'is_archived' in data:
        appointment.is_archived = data['is_archived']

    fields_to_update = ['appointment_status', 'last_updated_by', 'last_update_reason']
    if 'appointed_date' in data:
        fields_to_update.append('appointed_date')
    if 'appointed_time' in data:
        fields_to_update.append('appointed_time')
    if 'is_archived' in data:
        fields_to_update.append('is_archived')


    appointment.save(update_fields=fields_to_update)

def get_appointment_context(appointment, user_info, form=None, error=None):
    if form is None:
        form = MoveAppointmentForm(deputy=appointment.deputy, instance=appointment)
    
    return {
        'appointment': appointment,
        'form': form,
        'themes': AppointmentTheme.objects.all(),
        'user_info': user_info,
        'can_move': can_move_appointment(appointment),
        'active_page': 'appointments_manage',
        'error': error,
    }

def render_appointment_get_request(request, appointment, user_info, can_move):
    print("NOT POST")
    return render(request, 'priemka/appointment_details.html', get_appointment_context(appointment, user_info))


# def appointment_details(request, appointment_id):
#     print("APPOINT DETAILS")
#     appointment = get_object_or_404(Appointment, pk=appointment_id)
#     user_info = {
#         'short_name': request.user.get_short_name(),
#         'full_name': request.user.get_full_name()
#     } if request.user.is_authenticated else None

#     current_time = timezone.now()
#     appointment_datetime = timezone.make_aware(
#         datetime.combine(appointment.appointed_date, appointment.appointed_time)
#     )
#     can_move = current_time < (appointment_datetime - timedelta(hours=1))

#     if request.method == 'POST':
#         if 'move_appointment' in request.POST:
#             print("POST")
#             if not can_move:
#                 print("NOT CAN MOVE")
#                 return render(request, 'priemka/appointment_details.html', {
#                     'appointment': appointment,
#                     'form': MoveAppointmentForm(deputy=appointment.deputy, instance=appointment),
#                     'themes': AppointmentTheme.objects.all(),
#                     'user_info': user_info,
#                     'error': 'Нельзя перенести запись менее чем за час до её начала.'
#                 })
            
#             form = MoveAppointmentForm(request.POST, deputy=appointment.deputy, instance=appointment)
#             if form.is_valid():
#                 print("VALID VALID VALID")
#                 appointment.appointed_date = form.cleaned_data['appointed_date']
#                 appointment.appointed_time = form.cleaned_data['appointed_time']
#                 appointment.last_updated_by = request.user
#                 appointment.last_update_reason = form.cleaned_data.get('update_reason', '')

#                 appointment.appointment_status = AppointmentStatus.objects.get(id=1)
#                 appointment.save(update_fields=['appointed_date', 'appointed_time', 'appointment_status', 'last_updated_by','last_update_reason'])
                
#                 if any(field in form.changed_data for field in ['appointed_date', 'appointed_time']):
#                     send_appointment_moved_notification (
#                         user=appointment.user,
#                         appointment=appointment,
#                         changed_by=request.user,
#                         update_reason=appointment.last_update_reason
#                     )
                
#                 print(f"Saved: {appointment.appointed_date}, {appointment.appointed_time}, {appointment.appointment_status}")
#                 return redirect('priemka_appointment_details_page', appointment_id=appointment.id)
#             else:
#                 print("FORM INVALID:", form.errors)

#         elif 'register_appointment' in request.POST:
#             update_reason = request.POST.get('update_reason', '')
#             print("POST REGISTER")
#             appointment.appointment_status = AppointmentStatus.objects.get(id=2)
#             appointment.last_updated_by = request.user
#             appointment.last_update_reason = update_reason

#             appointment.save(update_fields=['appointment_status', 'last_updated_by','last_update_reason'])
#             print(f"Registered: {appointment.appointment_status}")
#             return redirect('priemka_appointment_details_page', appointment_id=appointment.id)
        
#         elif 'finish_appointment' in request.POST:
#             update_reason = request.POST.get('update_reason', '')
#             print("POST FINISH")
#             appointment.appointment_status = AppointmentStatus.objects.get(id=3)
#             appointment.last_updated_by = request.user
#             appointment.last_update_reason = update_reason
#             appointment.is_archived = True
#             appointment.save(update_fields=['appointment_status', 'is_archived', 'last_updated_by','last_update_reason'])
#             print(f"Finished: {appointment.appointment_status}, Archived: {appointment.is_archived}")
#             return redirect('priemka_appointment_details_page', appointment_id=appointment.id)

#         elif 'cancel_appointment' in request.POST:
#             update_reason = request.POST.get('update_reason', '')
#             print("POST CANCEL")
#             appointment.appointment_status = AppointmentStatus.objects.get(id=4)
#             appointment.last_updated_by = request.user
#             appointment.last_update_reason = update_reason
#             appointment.is_archived = True
#             appointment.save(update_fields=['appointment_status', 'is_archived', 'last_updated_by','last_update_reason'])
#             print(f"Canceled: {appointment.appointment_status}, Archived: {appointment.is_archived}")
#             return redirect('priemka_appointment_details_page', appointment_id=appointment.id)
        
#         elif 'decline_appointment' in request.POST:
#             update_reason = request.POST.get('update_reason', '')
#             print("POST DECLINE")
#             appointment.appointment_status = AppointmentStatus.objects.get(id=5)
#             appointment.last_updated_by = request.user
#             appointment.last_update_reason = update_reason
#             appointment.is_archived = True
#             appointment.save(update_fields=['appointment_status', 'is_archived', 'last_updated_by','last_update_reason'])
#             print(f"Declined: {appointment.appointment_status}, Archived: {appointment.is_archived}")
#             return redirect('priemka_appointment_details_page', appointment_id=appointment.id)
#     else:
#         print("NOT POST")
#         form = MoveAppointmentForm(deputy=appointment.deputy, instance=appointment)

#     themes = AppointmentTheme.objects.all()
    
#     context = {
#         'appointment': appointment,
#         'form': form,
#         'themes': themes,
#         'user_info': user_info,
#         'can_move': can_move,
#         'active_page':"appointments_manage",
#     }

#     return render(request, 'priemka/appointment_details.html', context)

#################################### КОНЕЦ рефакторинг страница детали записи ###########################################

def appointment_success(request):
    return render(request, 'priemka/appointment_success.html')

