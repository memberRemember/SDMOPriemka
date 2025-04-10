from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from ..forms import *
from ..email_notifications import *
from ..models import *


@login_required
def priemka_lc_decisions_deputy(request):
    context = {
        'active_page': 'decisions_deputy',
    }
    
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
        status_filter = request.GET.get('status', 'all')
        user_filter = request.GET.get('user', 'all')

        queryset = Decision.objects.filter(deputy=deputy) if deputy else Decision.objects.all()

        if filter_type == 'archived':
            queryset = queryset.filter(is_archived=True)
        else:
            queryset = queryset.filter(is_archived=False)
        
        if status_filter != 'all':
            queryset = queryset.filter(status__id=int(status_filter))

        if user_filter != 'all':
            queryset = queryset.filter(appointment__user__id=int(user_filter))
        
        decisions_data = [
            {
                'id': decision.id,
                'user': f"{decision.appointment.user.last_name} {decision.appointment.user.first_name} {decision.appointment.user.patronymic_name}",
                'deputy': f"{decision.deputy.last_name} {decision.deputy.first_name} {decision.deputy.patronymic_name}",
                'appointment_date': decision.appointment.appointed_date.strftime('%d.%m.%Y'),
                'appointment_time': decision.appointment.appointed_time.strftime('%H:%M'),
                'theme': str(decision.appointment.appointment_theme),
                'text': decision.decision_text,
                'status_id': decision.status.id,
                'status_name': str(decision.status),
                'created_at': decision.created_at.strftime('%H:%M %d.%m.%Y'),
                'is_final': decision.is_final,
                'is_archived': decision.is_archived,
            }
            for decision in queryset
        ]
        
        return JsonResponse({'decisions': decisions_data})
    
    decisions = Decision.objects.filter(
        deputy=deputy,
        is_archived=False
    ) if deputy else Decision.objects.none()
    
    deputies = Deputy.objects.all()
    users = User.objects.filter(appointment__decision__isnull=False).distinct()


    context['deputies'] = deputies
    context['decisions'] = decisions
    context['filter_type'] = 'actual'
    context['users'] = users

    return render(request, 'priemka/priemka_lc_decisions_manage.html', context)

@login_required
def priemka_lc_decisions(request):
    context = {
        'active_page': 'decisions',
    }
    
    if request.user.is_authenticated:
        context['user_info'] = {
            'short_name': request.user.get_short_name(),
            'full_name': request.user.get_full_name()
        }
    
    try:
        deputies = Deputy.objects.filter(decision__appointment__user=request.user).distinct()
    except Deputy.DoesNotExist:
        deputies = None
    

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        filter_type = request.GET.get('filter', 'actual')
        status_filter = request.GET.get('status', 'all')
        deputy_filter = request.GET.get('deputy', 'all')

        queryset = Decision.objects.filter(appointment__user__id=request.user.id)
        
        if filter_type == 'archived':
            queryset = queryset.filter(is_archived=True)
        else:
            queryset = queryset.filter(is_archived=False)
        
        if status_filter != 'all':
            queryset = queryset.filter(status__id=int(status_filter))

        if deputy_filter != 'all':
            queryset = queryset.filter(deputy=int(deputy_filter))
        
        decisions_data = [
            {
                'id': decision.id,
                'user': f"{decision.appointment.user.last_name} {decision.appointment.user.first_name} {decision.appointment.user.patronymic_name}",
                'deputy': f"{decision.deputy.last_name} {decision.deputy.first_name} {decision.deputy.patronymic_name}",
                'appointment_date': decision.appointment.appointed_date.strftime('%d.%m.%Y'),
                'appointment_time': decision.appointment.appointed_time.strftime('%H:%M'),
                'appointment_title': decision.appointment.title,
                'appointment_description': decision.appointment.description,
                'theme': str(decision.appointment.appointment_theme),
                'text': decision.decision_text,
                'status_id': decision.status.id,
                'status_name': str(decision.status),
                'created_at': decision.created_at.strftime('%H:%M %d.%m.%Y'),
                'is_final': decision.is_final,
                'is_archived': decision.is_archived,
            }
            for decision in queryset
        ]
        
        return JsonResponse({'decisions': decisions_data})
    
    
    context['deputies'] = deputies

    context['filter_type'] = 'actual'
    return render(request, 'priemka/priemka_lc_decisions.html', context)



################################## START DECISIONS DETAILS ###########################################
@login_required
def decision_details(request, decision_id):
    decision = get_object_or_404(Decision, pk=decision_id)
    user_info = get_user_info(request.user) if request.user.is_authenticated else None
    can_edit = can_edit_decision(decision)
    print(can_edit)

    if request.method == 'POST':
        return handle_decision_post_request(request, decision, user_info, can_edit)
    
    return render_dicision_get_request(request, decision, user_info, can_edit)

def get_user_info(user):
    return {
        'short_name': user.get_short_name(),
        'full_name': user.get_full_name()
    }

def can_edit_decision(decision):
    return not decision.is_final and not decision.is_archived

def handle_decision_post_request(request, decision, user_info, can_edit):
    actions = {
        'accept_decision': handle_accept_decision,
        'work_decision': handle_work_decision,
        'finish_decision': handle_final_decision,
        'decline_decision': handle_decline_decision,
        'edit_decision': handle_edit_decision,
        'done_decision': handle_done_decision,
    }

    for action, handler in actions.items():
        if action in request.POST:
            return handler(request, decision, user_info, can_edit)
    
    return render(request, 'priemka/decision_details.html', get_decision_context(decision, user_info, error="Неизвестное действие"))

def handle_accept_decision(request, decision, user_info, can_edit):
    if decision.status.id != 1:
        return render(request, 'priemka/decision_details.html', get_decision_context(
            decision, user_info, error="Нельзя изменить это решение."
        ))
    print("POST ACCEPT")
    update_decision(decision, {}, status_id=2, request_user=request.user)
    print(f"Accepted: {decision.status}")
    return redirect('priemka_lc_decisions_details_page', decision_id=decision.id)

def handle_work_decision(request, decision, user_info, can_edit):
    if decision.status.id !=2:
        return render(request, 'priemka/decision_details.html', get_decision_context(
            decision, user_info, error="Нельзя изменить это решение."
        ))
    print("POST WORK")
    update_decision(decision, {}, status_id=3, request_user=request.user)
    print(f"In Work: {decision.status}")
    return redirect('priemka_lc_decisions_details_page', decision_id=decision.id)

def handle_final_decision(request, decision, user_info, can_edit):
    if not can_edit:
        return render(request, 'priemka/decision_details.html', get_decision_context(
            decision, user_info, error="Нельзя изменить это решение."
        ))
    print("POST FINISH")
    update_decision(decision, {'is_final': True}, request_user=request.user)
    print(f"Final decision: {decision.is_final}")
    return redirect('priemka_lc_decisions_details_page', decision_id=decision.id)

def handle_done_decision(request, decision, user_info, can_edit):
    if decision.status.id !=3:
        return render(request, 'priemka/decision_details.html', get_decision_context(
            decision, user_info, error="Нельзя изменить это решение."
        ))
    print("POST DONE")
    update_decision(decision, {'is_archived': True}, status_id=4, request_user=request.user)
    print(f"Done: {decision.status}, Archived: {decision.is_archived}")
    return redirect('priemka_lc_decisions_details_page', decision_id=decision.id)


def handle_decline_decision(request, decision, user_info, can_edit):
    if not can_edit and decision.status.id not in [1,2]:
        return render(request, 'priemka/decision_details.html', get_decision_context(
            decision, user_info, error="Нельзя изменить это решение."
        ))
    print("POST DECLINE")
    update_decision(decision, {'is_archived': True}, status_id=5, request_user=request.user)
    print(f"Declined: {decision.status}, Archived: {decision.is_archived}")
    return redirect('priemka_lc_decisions_details_page', decision_id=decision.id)

def handle_edit_decision(request, decision, user_info, can_edit):
    if not can_edit:
        return render(request, 'priemka/decision_details.html', get_decision_context(
            decision, user_info, error="Нельзя изменить это решение."
        ))
    print("POST EDIT")
    form = EditDecisionForm(request.POST, instance=decision)
    if form.is_valid():
        update_decision(decision, {'decision_text': form.cleaned_data['decision_text']}, status_id=decision.status.id, request_user=request.user)
        print(f"Edited: {decision.decision_text}")
        return redirect('priemka_lc_decisions_details_page', decision_id=decision.id)
    print("FORM INVALID:", form.errors)
    return render(request, 'priemka/decision_details.html', get_decision_context(decision, user_info, form=form))

def update_decision(decision, data, request_user, status_id=None):

    decision_fields = []

    if not status_id == None:
        decision.status = DecisionStatus.objects.get(id=status_id)
        decision_fields.append('status')

    decision.appointment.last_updated_by = request_user
    decision.updated_by = request_user
    decision.updated_at = datetime.now()

    if 'decision_text' in data:
        decision.decision_text = data['decision_text']
    if 'is_archived' in data:
        decision.is_archived = data['is_archived']
    if 'is_final' in data:
        decision.is_final = data['is_final']

    if 'decision_text' in data:
        decision_fields.append('decision_text')
    if 'is_archived' in data:
        decision_fields.append('is_archived')
    if 'is_final' in data:
        decision_fields.append('is_final')
    decision_fields.append('updated_at')
    decision_fields.append('updated_by')
    decision.save(update_fields=decision_fields)

    decision.appointment.save(update_fields=['last_updated_by'])

    send_decision_status_notification (
        user=decision.appointment.user,
        appointment=decision.appointment,
        decision=decision,
        deputy=decision.deputy
    )

def get_decision_context(decision, user_info, form=None, error=None):
    if form is None:
        form = EditDecisionForm(instance=decision)
    
    return {
        'decision': decision,
        'appointment': decision.appointment,
        'form': form,
        'user_info': user_info,
        'can_edit': can_edit_decision(decision),
        'active_page': 'decisions_deputy',
        'error': error,
    }

def render_dicision_get_request(request, decision, user_info, can_edit):
    print("NOT POST")
    return render(request, 'priemka/decision_details.html', get_decision_context(decision, user_info))

################################## END DECISIONS DETAILS ###########################################



@login_required
def decision_creation(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    deputy = get_object_or_404(Deputy, user=request.user)

    if request.user.is_authenticated:
        user_info = {
            'short_name': request.user.get_short_name(),
            'full_name': request.user.get_full_name()
        }
    else:
        return redirect('login')

    if request.method == 'POST':
        form = DecisionForm(request.POST, appointment=appointment, deputy=deputy)
        if form.is_valid():
            decision = form.save(commit=False)
            decision.appointment = appointment
            decision.deputy = deputy
            decision.status_id = 1
            
            if form.cleaned_data['is_final']:
                decision.status_id = 4
                decision.is_archived = True
            
            decision.save()

            try:
                appointment.appointment_status = AppointmentStatus.objects.get(id=3)
                appointment.is_archived = True
                appointment.save(update_fields=['appointment_status','is_archived'])
            except Exception as e:
                print(f'Ошибка при завершении записи - {str(e)}')
            
            send_decision_notification(
                user=appointment.user,
                appointment=appointment,
                decision=decision,
                deputy=deputy
            )
            
            return redirect('priemka_lc_decisions_details_page', decision_id=decision.id)
    else:
        form = DecisionForm(appointment=appointment, deputy=deputy)
    
    return render(request, 'priemka/decision_creation.html', {
        'appointment': appointment,
        'form': form,
        'user_info': user_info,
    })

