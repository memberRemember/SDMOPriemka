from django.db import models
from pgtrigger import *
from django.contrib.auth.models import AbstractBaseUser, AbstractUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
import random


class Role(models.Model):
    rolename = models.CharField(max_length=25, null=False, unique=True, db_index=True, verbose_name="Название роли")

    def __str__(self):
        return self.rolename

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"


class ElectoralDistrict(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True, db_index=True, verbose_name="Название округа")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Избирательный округ"
        verbose_name_plural = "Избирательные округа"


class AppointmentTheme(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True, db_index=True, verbose_name="Название темы")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тема приема"
        verbose_name_plural = "Темы приема"


class AppointmentStatus(models.Model):
    name = models.CharField(max_length=50, null=False, unique=True, db_index=True, verbose_name="Название статуса")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Статус приема"
        verbose_name_plural = "Статусы приема"


class DecisionStatus(models.Model):
    name = models.CharField(max_length=50, null=False, unique=True, db_index=True, verbose_name="Название статуса")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Статус решения"
        verbose_name_plural = "Статусы решений"


class UserManager(BaseUserManager):
    def _create_user(self, login, password, **extra_fields):
        if not login:
            raise ValueError('The given login must be set')
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(login, password, **extra_fields)

    def create_superuser(self, login, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(login, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'login'

    login = models.CharField(max_length=25, null=False, unique=True, verbose_name="Логин")
    password = models.CharField(max_length=255, null=False, verbose_name="Пароль")
    last_name = models.CharField(max_length=50, blank=True, null=False, verbose_name="Фамилия")
    first_name = models.CharField(max_length=50, blank=True, null=False, verbose_name="Имя")
    patronymic_name = models.CharField(max_length=50, blank=True, null=True, default=" ", verbose_name="Отчество")
    email = models.EmailField(max_length=50, blank=True, null=True, verbose_name="Email")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, default=0, blank=True, null=False, verbose_name="Роль")

    creation_date = models.DateTimeField(auto_now=True, verbose_name="Дата создания")
    join_date = models.DateTimeField(default=timezone.now, verbose_name="Дата регистрации")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Сотрудник")
    is_superuser = models.BooleanField(default=False, verbose_name="Суперпользователь")

    receive_notifications = models.BooleanField(
        default=True,
        verbose_name="Получать уведомления по email"
    )

    objects = UserManager()

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        return f'{self.last_name} {self.first_name} {self.patronymic_name}'
    
    def get_pk(self):
        return str(self.pk)

    class Meta:
        index_together = ["login", "password", "last_name", "first_name", "patronymic_name"]
        triggers = [
            SoftDelete(name='user', field='is_active')
        ]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.login


class Deputy(models.Model):
    last_name = models.CharField(max_length=50, blank=True, null=False, verbose_name="Фамилия")
    first_name = models.CharField(max_length=50, blank=True, null=False, verbose_name="Имя")
    patronymic_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Отчество")
    position = models.CharField(max_length=255, blank=True, null=False, verbose_name="Должность")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    email = models.EmailField(max_length=50, blank=True, null=True, verbose_name="Email")
    electoral_district = models.ForeignKey(ElectoralDistrict, on_delete=models.PROTECT, blank=True, null=False, verbose_name="Избирательный округ")
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Пользователь")
    image = models.CharField(max_length=255, blank=True, null=True, verbose_name="Изображение")

    def get_short_name(self):
        return f'{self.last_name} {self.first_name}'

    def get_full_name(self):
        return f'{self.last_name} {self.first_name} {self.patronymic_name}'
    
    def get_pk(self):
        return str(self.pk)

    class Meta:
        index_together = ["last_name", "first_name", "patronymic_name", "position", "electoral_district"]
        verbose_name = "Депутат"
        verbose_name_plural = "Депутаты"

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic_name}'


class Appointment(models.Model):
    deputy = models.ForeignKey(Deputy, on_delete=models.PROTECT, blank=False, null=False, verbose_name="Депутат")
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=False, null=False, verbose_name="Пользователь")
    title = models.CharField(max_length=50, blank=False, null=False, verbose_name="Заголовок")
    appointment_theme = models.ForeignKey(AppointmentTheme, on_delete=models.PROTECT, blank=False, null=False, verbose_name="Тема приема")
    description = models.TextField(blank=False, null=True, verbose_name="Описание")
    creation_date = models.DateTimeField(auto_now=True, verbose_name="Дата создания")
    appointed_date = models.DateField(null=False, verbose_name="Дата приема")
    appointed_time = models.TimeField(null=False, default="08:30", verbose_name="Время приема")
    appointment_status = models.ForeignKey(AppointmentStatus, on_delete=models.PROTECT, blank=False, null=False, default=1, verbose_name="Статус приема")
    is_archived = models.BooleanField(default=False, blank=True, verbose_name="Архивировано")
    last_updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='modified_appointments', 
        null=True,
        blank=True,
        verbose_name="Кто изменил запись"
    )
    last_update_reason = models.TextField(
        blank=True,
        verbose_name="Причина изменения"
    )

    class Meta:
        index_together = ["deputy", "user", "title", "appointment_theme", "appointed_date", "appointed_time"]
        triggers = [
            SoftDelete(name='appointment', field='is_archived', value=True)
        ]
        verbose_name = "Запись на прием"
        verbose_name_plural = "Записи на прием"

    def __str__(self):
        return f'{self.deputy} {self.title} {self.appointed_date} {self.appointed_time}'


class Decision(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.PROTECT, blank=False, null=False, verbose_name="Запись на прием")
    deputy = models.ForeignKey(Deputy, on_delete=models.PROTECT, blank=False, null=False, verbose_name="Депутат")
    decision_text = models.TextField(blank=False, null=False, verbose_name="Текст решения")
    status = models.ForeignKey(DecisionStatus, on_delete=models.PROTECT, blank=False, null=False, default=1, verbose_name="Статус решения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='modified_decision', null=True, blank=True, verbose_name="Кто изменил запись")
    is_final = models.BooleanField(default=False, verbose_name="Решение окончательное")
    is_archived = models.BooleanField(default=False, blank=True, verbose_name="Архивировано")

    class Meta:
        index_together = ["appointment", "deputy", "created_at"]
        triggers = [
            SoftDelete(name='decision', field='is_archived', value=True)
        ]
        verbose_name = "Решение"
        verbose_name_plural = "Решения"

    def __str__(self):
        return f"Решение по {self.appointment} от {self.deputy} ({self.created_at})"


class DeputySchedule(models.Model):
    deputy = models.ForeignKey(Deputy, on_delete=models.PROTECT, blank=False, null=False, verbose_name="Депутат")
    start_time = models.TimeField(blank=False, null=False, verbose_name="Время начала")
    end_time = models.TimeField(blank=False, null=False, verbose_name="Время окончания")
    break_start = models.TimeField(null=True, blank=True, verbose_name="Начало перерыва")
    break_end = models.TimeField(null=True, blank=True, verbose_name="Окончание перерыва")  
    is_available = models.BooleanField(default=False, blank=True, verbose_name="Доступен")

    DAYS_OF_WEEK = [
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота'),
        (7, 'Воскресенье'),
    ]
    
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, verbose_name="День недели")
    
    def get_day_of_week_display(self):
        return dict(self.DAYS_OF_WEEK).get(self.day_of_week, '')

    class Meta:
        index_together = ["deputy", "day_of_week", "start_time", "end_time", "is_available"]
        verbose_name = "Расписание депутата"
        verbose_name_plural = "Расписания депутатов"

    def __str__(self):
        return f'{self.deputy} {self.day_of_week} {self.start_time} {self.end_time}'


class EmailConfirmation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    email = models.EmailField(verbose_name="Email")
    code = models.CharField(max_length=6, verbose_name="Код подтверждения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_confirmed = models.BooleanField(default=False, verbose_name="Подтверждено")

    @classmethod
    def create_confirmation(cls, user, email):
        cls.objects.filter(user=user, email=email).delete()
        
        code = str(random.randint(100000, 999999))
        
        confirmation = cls.objects.create(
            user=user,
            email=email,
            code=code
        )
        context = {
            'user': user,
            'email': email,
            'code': code,
            'current_year': timezone.now().year
        }

        html_content = render_to_string('email_templates/emailconfirmation_template.html', context)

        try:
            print("ОТПРАВКА В МОДЕЛИ")
            msg = EmailMultiAlternatives(
                subject="Подтверждение email",
                from_email="sdmopriemka@ya.ru",
                to=[email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            confirmation.delete()
            raise Exception(f'Не удалось отправить email: {str(e)}')
        
        return confirmation

    class Meta:
        verbose_name = "Подтверждение email"
        verbose_name_plural = "Подтверждения email"

    def __str__(self):
        return f"Подтверждение для {self.user} ({self.email})"


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_chats', verbose_name="Пользователь")
    secretary = models.ForeignKey(User, on_delete=models.CASCADE, related_name='secretary_chats', verbose_name="Секретарь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    class Meta:
        index_together = ["user", "secretary", "created_at", "is_active"]
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"

    def get_pk(self):
        return str(self.pk)
    
    def __str__(self):
        return f'Чат {self.pk} (Пользователь: {self.user.login}, Секретарь: {self.secretary.login})'


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', verbose_name="Чат")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Отправитель")
    text = models.TextField(verbose_name="Текст сообщения")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время отправки")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")

    class Meta:
        index_together = ["chat", "sender", "timestamp", "is_read"]
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def get_pk(self):
        return str(self.pk)
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'is_me': self.sender != self.chat.user,
            'is_read': self.is_read,
            'timestamp': self.timestamp.strftime("%H:%M %d.%m.%Y")
        }
    
    def __str__(self):
        return f'Сообщение {self.pk} (Чат: {self.chat.pk}, Отправитель: {self.sender.login})'