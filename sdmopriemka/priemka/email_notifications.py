from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import EmailConfirmation, Deputy, User

def send_email(subject, to_emails, html_content):
    """Отправляет письмо и возвращает результат."""
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_emails
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print(f"Уведомление отправлено на {', '.join(to_emails)}")
        return True
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")
        return False

def can_send_email(user):
    """Проверяет, можно ли отправить email пользователю."""
    if not user.email or not user.receive_notifications:
        return False
    return EmailConfirmation.objects.filter(
        user=user, email=user.email, is_confirmed=True
    ).exists()

def prepare_context(user, appointment, deputy, decision=None, changed_by=None, update_reason=""):
    """Формирует контекст для шаблонов."""
    return {
        'user': user,
        'appointment': appointment,
        'deputy': deputy,
        'decision': decision,
        'changed_by': changed_by,
        'update_reason': update_reason,
        'is_staff':False,
    }

def send_appointment_notification(user, appointment, deputy):
    """Отправляет уведомление о создании записи."""
    context = prepare_context(user, appointment, deputy)
    any_sent = False

    # Для посетителя
    if can_send_email(user):
        html_content = render_to_string('email_templates/newappointment_template.html', context)
        any_sent |= send_email(
            subject=f"Новая запись на приём к {deputy.get_full_name()}",
            to_emails=[user.email],
            html_content=html_content
        )

    # Для депутата
    deputy_emails = []
    if deputy.email:
        deputy_emails.append(deputy.email)
    if deputy.user and can_send_email(deputy.user):
        deputy_emails.append(deputy.user.email)

    if deputy_emails:
        html_content = render_to_string('email_templates/newappointment_deputy_template.html', context)
        any_sent |= send_email(
            subject=f"Новая запись на приём от {user.get_full_name()}",
            to_emails=deputy_emails,
            html_content=html_content
        )

    return any_sent

def send_decision_notification(user, appointment, decision, deputy):

    context = prepare_context(user, appointment, deputy, decision=decision)
    any_sent = False

    # Для посетителя
    if can_send_email(user):
        html_content = render_to_string('email_templates/newdecision_template.html', context)
        any_sent |= send_email(
            subject=f"Было вынесено решение по вашему вопросу от {appointment.appointed_date.strftime('%m.%d.%Y')} {appointment.appointed_time.strftime('%H:%M')}",
            to_emails=[user.email],
            html_content=html_content
        )

    # Для депутата
    deputy_emails = []
    if deputy.email:
        deputy_emails.append(deputy.email)
    if deputy.user and can_send_email(deputy.user):
        deputy_emails.append(deputy.user.email)

    if deputy_emails:
        html_content = render_to_string('email_templates/newdecision_deputy_template.html', context)
        any_sent |= send_email(
            subject=f"Решение вопросу от {appointment.appointed_date.strftime('%m.%d.%Y')} {appointment.appointed_time.strftime('%H:%M')}",
            to_emails=deputy_emails,
            html_content=html_content
        )

    return any_sent

def send_appointment_status_notification(user, appointment, deputy):
    """Отправляет уведомление об изменении статуса записи."""
    context = prepare_context(user, appointment, deputy)
    any_sent = False

    # Для посетителя
    if can_send_email(user):
        html_content = render_to_string('email_templates/updatedappointment_template.html', context)
        any_sent |= send_email(
            subject=f"Изменение статуса записи на приём к {deputy.get_full_name()}",
            to_emails=[user.email],
            html_content=html_content
        )

    # Для депутата
    deputy_context = {
        **context,
        'is_staff':True
    }
    deputy_emails = []
    if deputy.email:
        deputy_emails.append(deputy.email)
    if deputy.user and can_send_email(deputy.user):
        deputy_emails.append(deputy.user.email)

    if deputy_emails:
        html_content = render_to_string('email_templates/updatedappointment_template.html', deputy_context)
        any_sent |= send_email(
            subject=f"Изменение статуса записи на приём от {user.get_full_name()}",
            to_emails=deputy_emails,
            html_content=html_content
        )

    return any_sent

def send_decision_status_notification(user, appointment, decision, deputy):

    context = prepare_context(user, appointment, deputy, decision=decision)
    any_sent = False

    # Для посетителя
    if can_send_email(user):
        html_content = render_to_string('email_templates/updateddecision_template.html', context)
        any_sent |= send_email(
            subject=f"Изменение решения во Вашему вопросу от {appointment.appointed_date.strftime('%m.%d.%Y')} {appointment.appointed_time.strftime('%H:%M')}",
            to_emails=[user.email],
            html_content=html_content
        )

    # Для депутата
    deputy_context = {
        **context,
        'is_staff':True
    }
    deputy_emails = []
    if deputy.email:
        deputy_emails.append(deputy.email)
    if deputy.user and can_send_email(deputy.user):
        deputy_emails.append(deputy.user.email)

    if deputy_emails:
        html_content = render_to_string('email_templates/updateddecision_template.html', deputy_context)
        any_sent |= send_email(
            subject=f"Изменение решения во вопросу от {appointment.appointed_date.strftime('%m.%d.%Y')} {appointment.appointed_time.strftime('%H:%M')}",
            to_emails=deputy_emails,
            html_content=html_content
        )

    return any_sent

def send_appointment_moved_notification(user, appointment, changed_by=None, update_reason=""):
    if not can_send_email(user):
        return False
    
    context = prepare_context(user, appointment, appointment.deputy, changed_by, update_reason)
    html_content = render_to_string('email_templates/appointment_moved.html', context)
    
    return send_email(
        subject=f"Перенос записи на приём к {appointment.deputy.get_full_name()}",
        to_emails=[user.email],
        html_content=html_content
    )