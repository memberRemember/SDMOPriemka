from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.forms import *
from django.contrib.auth.views import *
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import *
from django.contrib.auth.decorators import login_required
from priemka.models import *
from ..forms import *
import json
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from ..email_notifications import *
from datetime import datetime, timedelta

from django.db.models import Count, Q
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os
from transliterate import translit

def test_email(request):
    changed_by = {
        'role':'Секретарь',
        'last_name':'Васильев',
        'first_name':'Василий',
        'patronymic_name':'Васильевич',
    }
    update_reason = 'просто так'

    deputy = {
        'id':11,
        'role':'Депутат',
        'last_name':'Иванов',
        'first_name':'Иван',
        'patronymic_name':'Иванович',
        'user': request.user,
    }

    appointment = {
        'id':481,
        'user':request.user,
        'deputy':deputy,
        'title':'Тестирование увед',
        'appointment_theme':'Тестирование увед',
        'description':'Тестирование увед описание',
        'appointed_date':'04.02.2025',
        'appointed_time':'08:30',
        'appointment_status':'В обработке',
    }

    decision = {
        'appointment':appointment,
        'deputy':deputy,
        'decision_text':'Посмотрим, ченить придумаем. Дадим знать зуб даю.',
        'created_at':'07.04.2025',
        'updated_at':'07-04-2025',
        'updated_by':deputy,
        'status':'На рассмотрении',
        'is_final':False,
        'is_archived': False
    }

    context = {
        'deputy':deputy,
        'appointment': appointment,
        'changed_by':changed_by,
        'update_reason':update_reason,
        'decision':decision

    }
    return render(request, 'email_templates/updateddecision_template.html', context)

def priemka_index(request):
    context = {}
    
    if request.user.is_authenticated:
        context['user_info'] = {
            'short_name': request.user.get_short_name(),
            'full_name': request.user.get_full_name()
        }
        if request.user.role.id == 3:
            return redirect('priemka_lc_appointments_deputy_page')
    
    deputies = Deputy.objects.all().select_related('electoral_district') if Deputy.objects.exists() else None
    context['deputies'] = deputies
    
    return render(request, 'priemka/priemka_index.html', context)


# def priemka_lc_appointments(request):
#     context = {}
    
#     if request.user.is_authenticated:
#         context['user_info'] = {
#             'short_name': request.user.get_short_name(),
#             'full_name': request.user.get_full_name()
#         }
    
#     deputies = Deputy.objects.all()
#     appointments = Appointment.objects.all()
#     context['deputies'] = deputies
#     context['appointments'] = appointments
    
#     return render(request, 'priemka/priemka_lc_appointments.html', context)







# def priemka_lc_appointments(request):
#     context = {
#         'active_page':'appointments',
#     }
    
#     if request.user.is_authenticated:
#         context['user_info'] = {
#             'short_name': request.user.get_short_name(),
#             'full_name': request.user.get_full_name()
#         }

#     try:
#         deputies = Deputy.objects.filter(appointment__user=request.user).distinct()
#     except Deputy.DoesNotExist:
#         deputies = None


#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         filter_type = request.GET.get('filter', 'actual')
#         status_filter = request.GET.get('status', 'all')
#         deputy_filter = request.GET.get('deputy', 'all')
#         search_id = request.GET.get('search_id', '')

#         queryset = Appointment.objects.filter(user=request.user)

#         if filter_type == 'archived':
#             queryset = queryset.filter(is_archived=True)
#         else:
#             queryset = queryset.filter(is_archived=False)
        
        
#         if status_filter != 'all':
#             queryset = queryset.filter(appointment_status__id=int(status_filter))

#         if deputy_filter != 'all':
#             queryset = queryset.filter(deputy=int(deputy_filter))

#         if search_id:
#             queryset = queryset.filter(id__startswith=search_id)
        
#         appointments_data = [
#             {
#                 'id': appointment.id,
#                 'deputy': f"{appointment.deputy.last_name} {appointment.deputy.first_name} {appointment.deputy.patronymic_name}",
#                 'position': appointment.deputy.position,
#                 'theme': str(appointment.appointment_theme),
#                 'title': appointment.title,
#                 'appointed_date': appointment.appointed_date.strftime('%d.%m.%Y'),
#                 'appointed_time': appointment.appointed_time.strftime('%H:%M'),
#                 'creation_date': appointment.creation_date.strftime('%H:%M %d.%m.%y'),
#                 'status_id': appointment.appointment_status.id,
#                 'status_name': str(appointment.appointment_status),
#             }
#             for appointment in queryset
#         ]
        
#         return JsonResponse({'appointments': appointments_data})
    
    
#     appointments = Appointment.objects.filter(user=request.user, is_archived=False)
    
#     context['deputies'] = deputies
#     context['appointments'] = appointments
#     context['filter_type'] = 'actual'
#     # context['active_page'] = "appointments",
    
#     return render(request, 'priemka/priemka_lc_appointments.html', context)

# def priemka_lc_appointments_manage(request):
#     context = {
#         'active_page':'appointments_manage',
#     }
    
#     if request.user.is_authenticated:
#         context['user_info'] = {
#             'short_name': request.user.get_short_name(),
#             'full_name': request.user.get_full_name()
#         }
    
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         filter_type = request.GET.get('filter', 'actual')
#         status_filter = request.GET.get('status', 'all')
#         user_filter = request.GET.get('user', 'all')
#         search_id = request.GET.get('search_id', '')

#         queryset = Appointment.objects.all().select_related('user', 'deputy', 'appointment_status')

#         if filter_type == 'archived':
#             queryset = queryset.filter(is_archived=True)
#         else:
#             queryset = queryset.filter(is_archived=False)
        
#         if status_filter != 'all':
#             queryset = queryset.filter(appointment_status__id=int(status_filter))

#         if user_filter != 'all':
#             queryset = queryset.filter(user__id=int(user_filter))

#         if search_id:
#             queryset = queryset.filter(id__startswith=search_id)
        
#         appointments_data = [
#             {
#                 'id': appointment.id,
#                 'user': f"{appointment.user.last_name} {appointment.user.first_name} {appointment.user.patronymic_name}",
#                 'deputy': f"{appointment.deputy.last_name} {appointment.deputy.first_name} {appointment.deputy.patronymic_name}",
#                 'position': appointment.deputy.position,
#                 'theme': str(appointment.appointment_theme),
#                 'title': appointment.title,
#                 'appointed_date': appointment.appointed_date.strftime('%d.%m.%Y'),
#                 'appointed_time': appointment.appointed_time.strftime('%H:%M'),
#                 'creation_date': appointment.creation_date.strftime('%H:%M %d.%m.%y'),
#                 'status_id': appointment.appointment_status.id,
#                 'status_name': str(appointment.appointment_status),
#             }
#             for appointment in queryset
#         ]
        
#         return JsonResponse({'appointments': appointments_data})
    
    
#     appointments = Appointment.objects.all().filter(is_archived=False)
#     deputies = Deputy.objects.all()
#     users = User.objects.filter(appointment__isnull=False).distinct()

#     context['deputies'] = deputies
#     context['appointments'] = appointments
#     context['filter_type'] = 'actual'
#     context['users'] = users
#     # context['active_page'] = "appointments",
    
#     return render(request, 'priemka/priemka_lc_appointments_manage.html', context)


# @login_required
# def priemka_lc_appointments_today_deputy(request):
    
#     context = {
#         'active_page': 'appointments_today_deputy',
#     }
    
#     if request.user.is_authenticated:
#         context['user_info'] = {
#             'short_name': request.user.get_short_name(),
#             'full_name': request.user.get_full_name()
#         }
    

#     try:
#         deputy = Deputy.objects.get(user=request.user)
#     except Deputy.DoesNotExist:
#         deputy = None
    
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         filter_type = request.GET.get('filter', 'actual')
#         status_filter = request.GET.get('status', '2') 
#         user_filter = request.GET.get('user', 'all')


#         queryset = Appointment.objects.filter(
#             deputy=deputy, 
#             appointment_status__id=2, 
#             appointed_date=datetime.today().strftime('%Y-%d-%m'), 
#             is_archived=False
#         ).order_by('appointed_time') if deputy else Appointment.objects.none()

#         if user_filter != 'all':
#             queryset = queryset.filter(user__id=int(user_filter))
        
#         appointments_data = [
#             {
#                 'id': appointment.id,
#                 'user': f"{appointment.user.last_name} {appointment.user.first_name} {appointment.user.patronymic_name}",
#                 'deputy': f"{appointment.deputy.last_name} {appointment.deputy.first_name} {appointment.deputy.patronymic_name}",
#                 'position': appointment.deputy.position,
#                 'theme': str(appointment.appointment_theme),
#                 'title': appointment.title,
#                 'appointed_date': appointment.appointed_date.strftime('%d.%m.%Y'),
#                 'appointed_time': appointment.appointed_time.strftime('%H:%M'),
#                 'creation_date': appointment.creation_date.strftime('%H:%M %d.%m.%y'),
#                 'status_id': appointment.appointment_status.id,
#                 'status_name': str(appointment.appointment_status),
#             }
#             for appointment in queryset
#         ]

        
#         return JsonResponse({'appointments': appointments_data})
    
#     appointments = Appointment.objects.filter(
#         deputy=deputy,
#         is_archived=False,
#         appointment_status__id=2,
#         appointed_date=datetime.today().strftime('%Y-%d-%m')
#     ).order_by('appointed_time') if deputy else Appointment.objects.none()

    
#     deputies = Deputy.objects.all()
#     users = User.objects.filter(appointment__isnull=False, appointment__appointed_date=datetime.today().strftime('%Y-%d-%m')).distinct()

#     context['deputies'] = deputies
#     context['appointments'] = appointments
#     context['filter_type'] = 'registered'
#     context['users'] = users

#     return render(request, 'priemka/priemka_lc_appointments_today_deputy.html', context)

# @login_required
# def priemka_lc_appointments_deputy(request):
    
#     context = {
#         'active_page': 'appointments_deputy',
#     }
    
#     if request.user.is_authenticated:
#         context['user_info'] = {
#             'short_name': request.user.get_short_name(),
#             'full_name': request.user.get_full_name()
#         }
    

#     try:
#         deputy = Deputy.objects.get(user=request.user)
#     except Deputy.DoesNotExist:
#         deputy = None
    
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         filter_type = request.GET.get('filter', 'registered')
#         status_filter = request.GET.get('status', 'all') 
#         user_filter = request.GET.get('user', 'all')
#         search_id = request.GET.get('search_id', '')


#         queryset = Appointment.objects.filter(deputy=deputy) if deputy else Appointment.objects.none()

#         if filter_type == 'archived':
#             queryset = queryset.filter(is_archived=True)
#         elif filter_type == 'registered':
#             queryset = queryset.filter(appointment_status=2, is_archived=False)
#         else:
#             queryset = queryset.filter(is_archived=False)
        
#         if status_filter != 'all':
#             queryset = queryset.filter(appointment_status__id=int(status_filter))

#         if user_filter != 'all':
#             queryset = queryset.filter(user__id=int(user_filter))

#         if search_id:
#             queryset = queryset.filter(id__startswith=search_id)
        
#         appointments_data = [
#             {
#                 'id': appointment.id,
#                 'user': f"{appointment.user.last_name} {appointment.user.first_name} {appointment.user.patronymic_name}",
#                 'deputy': f"{appointment.deputy.last_name} {appointment.deputy.first_name} {appointment.deputy.patronymic_name}",
#                 'position': appointment.deputy.position,
#                 'theme': str(appointment.appointment_theme),
#                 'title': appointment.title,
#                 'appointed_date': appointment.appointed_date.strftime('%d.%m.%Y'),
#                 'appointed_time': appointment.appointed_time.strftime('%H:%M'),
#                 'creation_date': appointment.creation_date.strftime('%H:%M %d.%m.%y'),
#                 'status_id': appointment.appointment_status.id,
#                 'status_name': str(appointment.appointment_status),
#             }
#             for appointment in queryset
#         ]
        
#         return JsonResponse({'appointments': appointments_data})
    
#     appointments = Appointment.objects.filter(
#         deputy=deputy,
#         is_archived=False,
#         appointment_status__id=2
#     ) if deputy else Appointment.objects.none()
    
#     users = User.objects.filter(appointment__isnull=False, appointment__deputy=deputy).distinct()

#     context['appointments'] = appointments
#     context['filter_type'] = 'registered'
#     context['users'] = users

#     return render(request, 'priemka/priemka_lc_appointments_deputy.html', context)


@login_required
def priemka_lc_statistics(request):
    context = {
        'active_page': 'statistics',
    }
    
    if request.user.is_authenticated:
        user_info = {
            'short_name': request.user.get_short_name(),
            'full_name': request.user.get_full_name()
        }
    
    try:
        deputy = Deputy.objects.get(user=request.user)
    except Deputy.DoesNotExist:
        deputy = None

    last_month = timezone.now() - timedelta(days=30)
    appointments_base = Appointment.objects.filter(creation_date__gte=last_month)
    decisions_base = Decision.objects.filter(created_at__gte=last_month)
    selected_deputy = None
    selected_deputy_id = request.GET.get('deputy', 'all')
    if selected_deputy_id != 'all':
        try:
            selected_deputy = Deputy.objects.get(id=selected_deputy_id)
            appointments_base = appointments_base.filter(deputy=selected_deputy)
            decisions_base = decisions_base.filter(deputy=selected_deputy)
        except Deputy.DoesNotExist:
            selected_deputy = None

    print(selected_deputy)

    total_appointments = appointments_base.count()
    resolved_decisions = decisions_base.filter(is_final=True, status__id=4).count()
    declined_decisions = decisions_base.filter(status__id=5).count()
    unresolved_decisions = decisions_base.filter(is_final=False).count()

    deputy_load = appointments_base.values(
        'deputy__last_name', 'deputy__first_name', 'deputy__patronymic_name'
    ).annotate(
        appointments_count=models.Count('id'),
        finished_count=models.Count('id', filter=models.Q(appointment_status__id=3)),
        resolved_count=models.Count('decision', filter=models.Q(decision__status__id=4, decision__is_final=True)),
        unresolved_count=models.Count('decision', filter=models.Q(decision__is_final=False)),
        declined_count=models.Count('decision', filter=models.Q(decision__status__id=5))
    )
    
    theme_stats = appointments_base.values('appointment_theme__name').annotate(
        count=models.Count('id')
    ).order_by('-count')

    decision_status_stats = decisions_base.values('status__name').annotate(
        count=models.Count('id')
    ).order_by('status__id')
    
    decisions = Decision.objects.filter(deputy=deputy, is_archived=False) if deputy else Decision.objects.none()
    deputies = Deputy.objects.all()

    if request.GET.get('export') == 'pdf':

        font_path = os.path.join(os.path.dirname(__file__), 'static', 'fonts', 'DejaVuSerif.ttf')
        font_path_bold = os.path.join(os.path.dirname(__file__), 'static', 'fonts', 'DejaVuSerif-Bold.ttf')
        font_path_italic = os.path.join(os.path.dirname(__file__), 'static', 'fonts', 'DejaVuSerif-Italic.ttf')
        font_path_bolditalic = os.path.join(os.path.dirname(__file__), 'static', 'fonts', 'DejaVuSerif-BoldItalic.ttf')

        print(f"Путь к шрифту: {font_path}")
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSerif', font_path))
            pdfmetrics.registerFont(TTFont('DejaVuSerif-Bold', font_path_bold))
            pdfmetrics.registerFont(TTFont('DejaVuSerif-Italic', font_path_italic))
            pdfmetrics.registerFont(TTFont('DejaVuSerif-BoldItalic', font_path_bolditalic))

            registerFontFamily('DejaVuSerif',
                normal='DejaVuSerif',
                bold='DejaVuSerif-Bold',
                italic='DejaVuSerif-Italic',
                boldItalic='DejaVuSerif-BoldItalic')
            print("Шрифт DejaVuSerif успешно зарегистрирован")
        except Exception as e:
            print(f"Ошибка регистрации шрифта: {e}")

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        styles['Normal'].fontName = 'DejaVuSerif'
        # styles['Heading1'].fontName = 'DejaVuSerif'
        # styles['Heading2'].fontName = 'DejaVuSerif'

        table_style = [
            ('FONT', (0, 0), (-1, -1), 'DejaVuSerif'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]

        title_style = ParagraphStyle(
            'yourtitle',
            fontName="Helvetica-Bold",
            fontSize=16,
            parent=styles['Heading2'],
            alignment=1,
            spaceAfter=14
        )
        # title_style = ParagraphStyle(
        #     name='DejaVuStyle',
        #     fontName='DejaVuSerif',
        #     fontSize=14,
        #     leading=16
        # )

        elements = []
        if not selected_deputy:
            elements.append(Paragraph("Статистика за последние 30 дней", ))
        else:
            elements.append(Paragraph(f"Статистика за последние 30 дней для депутата {selected_deputy.get_full_name()}", title_style))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Статус обращений", styles['Heading2']))
        status_data = [
            ["Всего записей на прием:", str(total_appointments)],
            ["Решено:", str(resolved_decisions)],
            ["В работе:", str(unresolved_decisions)],
            ["Отклонено:", str(declined_decisions)],
        ]
        status_table = Table(status_data)
        status_table.setStyle(table_style)
        elements.append(status_table)
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Загруженность депутатов", styles['Heading2']))
        deputy_data = [["Депутат", "Всего", "Завершено", "Решено", "В работе", "Не решено"]]
        for d in deputy_load:
            deputy_data.append([
                f"{d['deputy__last_name']} {d['deputy__first_name']} {d['deputy__patronymic_name'] or ''}",
                str(d['appointments_count']),
                str(d['finished_count']),
                str(d['resolved_count']),
                str(d['unresolved_count']),
                str(d['declined_count']),
            ])
        deputy_table = Table(deputy_data)
        deputy_table.setStyle(table_style)
        elements.append(deputy_table)
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Популярные темы обращений", styles['Heading2']))
        theme_data = [["Тема", "Количество"]]
        for t in theme_stats:
            theme_data.append([t['appointment_theme__name'], str(t['count'])])
        theme_table = Table(theme_data)
        theme_table.setStyle(table_style)
        elements.append(theme_table)
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Статистика решений по статусам", styles['Heading2']))
        status_stats_data = [["Статус", "Количество"]]
        for s in decision_status_stats:
            status_stats_data.append([s['status__name'], str(s['count'])])
        status_table = Table(status_stats_data)
        status_table.setStyle(table_style)
        elements.append(status_table)

        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()

        current_date = datetime.now().strftime('%d-%m-%Y')
        if not selected_deputy:
            filename = f"statistics_{current_date}.pdf"
        else:
            full_name_ru = selected_deputy.get_full_name()
            full_name_en = translit(full_name_ru, 'ru', reversed=True).replace(" ", "")
            filename = f"statistics_deputy-{full_name_en}_{current_date}.pdf"

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

   
    context = {
        'total_appointments': total_appointments,
        'resolved_decisions': resolved_decisions,
        'declined_decisions': declined_decisions,
        'unresolved_decisions': unresolved_decisions,
        'period': 'Последние 30 дней',
        'deputy_load': deputy_load,
        'theme_stats': theme_stats,
        'decision_status_stats': decision_status_stats,
        'user_info': user_info,
        'selected_deputy_id': selected_deputy_id,
        'deputies': deputies,
    }

    return render(request, 'priemka/priemka_lc_statistics.html', context)

# @login_required
# def priemka_lc_settings(request):
#     user = request.user

#     if request.user.is_authenticated:
#         user_info = {
#             'short_name': request.user.get_short_name(),
#             'full_name': request.user.get_full_name()
#         }
    
#     if request.method == 'POST':
#         if 'last_name' in request.POST:
#             user.last_name = request.POST.get('last_name', '')
#             user.first_name = request.POST.get('first_name', '')
#             patronymic = request.POST.get('patronymic_name', '')
#             user.patronymic_name = patronymic if patronymic else ' '
#             user.save()
#             return redirect('priemka_lc_settings_page')
        
#         if 'email' in request.POST:
#             user.email = request.POST.get('email', '')
#             user.save()
#             return redirect('priemka_lc_settings_page')
        
    
#     context = {
#         'user': user,
#         'user_info': user_info,
#         'active_page':"settings",
#     }
#     return render(request, 'priemka/priemka_lc_settings.html', context)
@login_required
def priemka_lc_settings(request):
    if not request.user.is_authenticated:
        return redirect('authuser')
    
    email_confirmed = False
    if request.user.email:
        email_confirmed = EmailConfirmation.objects.filter(
            user=request.user,
            email=request.user.email,
            is_confirmed=True
        ).exists()
    
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if 'email' in request.POST:
                form = EmailConfirmationForm(request.POST, user=request.user)
                if form.is_valid():
                    email = form.cleaned_data['email']
                    request.user.email = email
                    request.user.save()
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Email успешно обновлен'
                    })
                else:
                    errors = {}
                    for field, error_list in form.errors.items():
                        errors[field] = error_list[0]
                    
                    if hasattr(form, 'code_sent') and form.code_sent:
                        return JsonResponse({
                            'status': 'code_required'
                        })
                    
                    return JsonResponse({
                        'status': 'error',
                        'errors': errors
                    }, status=400)
            
            if 'receive_notifications' in request.POST:
                try:
                    receive_notifications = request.POST.get('receive_notifications') == 'true'
                    request.user.receive_notifications = receive_notifications
                    request.user.save()
                    
                    has_confirmed_email = EmailConfirmation.objects.filter(
                        user=request.user, 
                        email=request.user.email,
                        is_confirmed=True
                    ).exists()
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Настройки уведомлений обновлены',
                        'receive_notifications': receive_notifications,
                        'has_confirmed_email': has_confirmed_email
                    })
                except Exception as e:
                    return JsonResponse({
                        'status': 'error',
                        'message': str(e)
                    }, status=400)

        if 'last_name' in request.POST:
            user = request.user
            user.last_name = request.POST.get('last_name', '')
            user.first_name = request.POST.get('first_name', '')
            user.patronymic_name = request.POST.get('patronymic_name', ' ')
            user.save()
            messages.success(request, 'ФИО успешно обновлены')
            return redirect('priemka_lc_settings_page')
    
    context = {
        'active_page': 'settings',
        'user_info': {
            'short_name': request.user.get_short_name(),
            'full_name': request.user.get_full_name()
        },
        'email_confirmed': email_confirmed 
    }
    return render(request, 'priemka/priemka_lc_settings.html', context)


@login_required
def priemka_lc_deputy_profile(request):
    if not request.user.is_authenticated:
        return redirect('authuser')
    
    try:
        deputy = Deputy.objects.get(user=request.user)
    except Deputy.DoesNotExist:
        return redirect('priemka_index_page')

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if 'email' in request.POST:
            email = request.POST.get('email', '').strip()
            if email and not email.isspace():
                deputy.email = email
                deputy.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Email успешно обновлён'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email не может быть пустым'
                }, status=400)


        last_name = request.POST.get('last_name', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        patronymic_name = request.POST.get('patronymic_name', '').strip()
        position = request.POST.get('position', '').strip()
        description = request.POST.get('description', '').strip()
        electoral_district_id = request.POST.get('electoral_district', None)

        if not last_name or not first_name or not position or not electoral_district_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Обязательные поля (Фамилия, Имя, Должность, Избирательный округ) должны быть заполнены'
            }, status=400)

        try:
            electoral_district = ElectoralDistrict.objects.get(id=electoral_district_id)
        except ElectoralDistrict.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Выбранный избирательный округ не существует'
            }, status=400)

        deputy.last_name = last_name
        deputy.first_name = first_name
        deputy.patronymic_name = patronymic_name if patronymic_name else None
        deputy.position = position
        deputy.description = description if description else None
        deputy.electoral_district = electoral_district
        deputy.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Профиль успешно обновлён'
        })


    electoral_districts = ElectoralDistrict.objects.all()
    context = {
        'active_page': 'deputy_profile',
        'deputy': deputy,
        'electoral_districts': electoral_districts,
        'user_info': {
            'short_name': request.user.get_short_name(),
            'full_name': request.user.get_full_name()
        }
    }
    return render(request, 'priemka/priemka_lc_deputy_profile.html', context)


def admin_index(request):
    return render(request, 'admin/admin_index.html')


class RegisterUser(CreateView):
    form_class = CustomUserCreationForm
    template_name = './auth/registration.html'
    
    def get_success_url(self):
        if self.object.email:
            return reverse('email_confirmation')
        return reverse('authuser')

    def form_valid(self, form):
        response = super().form_valid(form)

        login(self.request, self.object)
        if self.object.email:
            messages.info(self.request, 'Проверьте вашу почту для подтверждения email')
        return response
    
class EmailConfirmationView(View):
    template_name = "auth/emailconfirmation.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('authuser')
        form = EmailConfirmationForm(user=request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('authuser')
            
        code = request.POST.get('code')
        try:
            confirmation = EmailConfirmation.objects.get(
                user=request.user,
                code=code,
                is_confirmed=False
            )
            
            EmailConfirmation.objects.filter(
                user=request.user,
                is_confirmed=False
            ).exclude(pk=confirmation.pk).delete()
            
            confirmation.is_confirmed = True
            confirmation.save()
            
            request.user.email = confirmation.email
            request.user.save()
            
            return redirect('priemka_index_page')
            
        except EmailConfirmation.DoesNotExist:
            return render(request, self.template_name, {
                'error': 'Неверный код подтверждения'
            })

# class AuthUser(LoginView):
#     form_class = CustomAuthenticationForm
#     template_name = './auth/login.html'
#     success_url = 'priemka_index_page'
#     def get_success_url(self):
#         return reverse_lazy('priemka_index_page')

class AuthUser(LoginView):
    form_class = CustomAuthenticationForm
    template_name = './auth/login.html'
    
    def get_success_url(self):
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        return next_url or reverse_lazy('priemka_index_page')
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
# class CustomLogoutView(LogoutView):
#     def get_success_url(self):
#         return reverse_lazy('index_page')
    
class CustomLogoutPriemkaView(LogoutView):
    def get_success_url(self):
        return reverse_lazy('priemka_index_page')
    

