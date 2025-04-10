from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Appointment
from .email_notifications import send_appointment_status_notification

@receiver(post_save, sender=Appointment)
def appointment_status_changed(sender, instance, created, **kwargs):
    update_fields = kwargs.get('update_fields')
    if not created and update_fields is not None and 'appointment_status' in update_fields:
        send_appointment_status_notification(
            user=instance.user,
            appointment=instance,
            deputy=instance.deputy
        )