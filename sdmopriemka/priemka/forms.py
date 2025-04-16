from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

User = get_user_model()


# class CustomUserCreationForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ['login', 'last_name', 'first_name', 'patronymic_name', 'email', ]


class CustomUserCreationForm(UserCreationForm):
    login = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Почта (необязательно)',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    patronymic_name = forms.CharField(
        label='Отчество (если есть)',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('login', 'email', 'last_name', 'first_name', 'patronymic_name')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise forms.ValidationError('Введите корректный адрес электронной почты')
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('Этот email уже используется')
        return email

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[а-яА-ЯёЁ-]+$', last_name):
            raise forms.ValidationError('Фамилия должна содержать только русские буквы и дефис')
        return last_name

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[а-яА-ЯёЁ-]+$', first_name):
            raise forms.ValidationError('Имя должно содержать только русские буквы и дефис')
        return first_name

    def clean_patronymic_name(self):
        patronymic_name = self.cleaned_data.get('patronymic_name')
        if patronymic_name: 
            if not re.match(r'^[а-яА-ЯёЁ-]+$', patronymic_name):
                raise forms.ValidationError('Отчество должно содержать только русские буквы и дефис')
        return patronymic_name

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        
        if commit:
            user.save()
            email = self.cleaned_data.get('email')
            if email:

                user.email = email
                user.save()

                EmailConfirmation.create_confirmation(user, email)
        
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'class': 'form-control',
            'placeholder': 'Введите ваш логин'
        })
    )
    password = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш пароль'
        })
    )

    error_messages = {
        'invalid_login': "Неверный логин или пароль.",
        'inactive': "Этот аккаунт неактивен.",
    }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if User.USERNAME_FIELD == 'login':
    #         self.fields['username'].widget.attrs['name'] = 'login'

    #     for field in self.fields.values():
    #         field.error_messages = {'required': 'Это поле обязательно для заполнения'}
    #         field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            try:
                user = User._default_manager.get_by_natural_key(username)
            except User.DoesNotExist:
                raise ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
            
            if not user.is_active:
                raise ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )
            
            if not user.check_password(password):
                raise ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
            
            self.user_cache = user

        return self.cleaned_data

    def get_user(self):
        return self.user_cache

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

    def clean_username(self):
        login = self.cleaned_data['login']
        if self.instance.pk:
            if User.objects.filter(login=login).exclude(pk=self.instance.pk).exists():
                raise ("Пользователь с таким логином уже существует.")
        return login
    
# class AppointmentForm(forms.ModelForm):
#     class Meta:
#         model = Appointment
#         fields = ['title', 'appointment_theme', 'description', 'appointed_date']
#         widgets = {
#             'title': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Краткое описание проблемы'
#             }),
#             'appointment_theme': forms.Select(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Выберите тему обращения'
#             }),
#             'description': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 4,
#                 'placeholder': 'Подробно опишите ваш вопрос'
#             }),
#             'appointed_date': forms.DateTimeInput(attrs={
#                 'class': 'form-control',
#                 'type': 'datetime-local'
#             })
#         }
#         labels = {
#             'title': 'Заголовок',
#             'appointment_theme': 'Тема обращения',
#             'description': 'Описание',
#             'appointed_date': 'Дата записи',
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['appointment_theme'].empty_label = 'Выберите тему обращения'
#         self.fields['appointment_theme'].queryset = AppointmentTheme.objects.all()

class AppointmentForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        label='Посетитель',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_user'
        })
    )

    class Meta:
        model = Appointment
        fields = ['title', 'appointment_theme', 'description', 'appointed_date', 'appointed_time']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Краткое описание проблемы'
            }),
            'appointment_theme': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Выберите тему обращения'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Подробно опишите ваш вопрос'
            }),
            'appointed_date': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_appointed_date'
            }),
            'appointed_time': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_appointed_time'
            }),
        }
        labels = {
            'title': 'Заголовок',
            'appointment_theme': 'Тема обращения',
            'description': 'Описание',
            'appointed_date': 'Дата записи',
            'appointed_time': 'Время записи',
        }

    def __init__(self, *args, deputy=None, user_role=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['appointment_theme'].empty_label = 'Выберите тему обращения'
        self.fields['appointment_theme'].queryset = AppointmentTheme.objects.all()

        self.user_role = user_role
        self.deputy = deputy

        if self.user_role not in [1, 2]:
            del self.fields['user']

        if deputy:
            available_dates = self.get_available_dates()
            self.fields['appointed_date'].widget.choices = [('', 'Выберите дату')] + available_dates

            self.fields['appointed_time'].widget.choices = [('', 'Сначала выберите дату')]
        else:
            self.fields['appointed_date'].widget.choices = [('', 'Нет доступных дат')]
            self.fields['appointed_time'].widget.choices = [('', 'Нет доступного времени')]

    def get_available_dates(self):
        """Получение списка доступных дат на основе расписания депутата."""
        if not self.deputy:
            return []

        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        available_dates = set()  # Используем set для уникальности

        schedules = DeputySchedule.objects.filter(deputy=self.deputy, is_available=True)
        for schedule in schedules:
            day_of_week = schedule.day_of_week
            for i in range(1, 31):  # Ограничение на 30 дней вперед
                target_date = tomorrow + timedelta(days=i)
                if target_date.weekday() + 1 == day_of_week:
                    available_dates.add((
                        target_date.strftime('%Y-%m-%d'),
                        target_date.strftime('%d.%m.%Y')
                    ))

        return sorted(list(available_dates), key=lambda x: x[0])

    def get_available_time_slots(self, selected_date):
        """Получение временных слотов для выбранной даты."""
        if not self.deputy or not selected_date:
            return []

        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            return []

        day_of_week = selected_date.weekday() + 1
        time_slots = []

        schedules = DeputySchedule.objects.filter(deputy=self.deputy, day_of_week=day_of_week, is_available=True)
        for schedule in schedules:
            start_time = schedule.start_time
            end_time = schedule.end_time
            break_start = schedule.break_start
            break_end = schedule.break_end

            current_time = datetime.combine(selected_date, start_time)
            end_datetime = datetime.combine(selected_date, end_time)

            while current_time < end_datetime:
                slot_end = current_time + timedelta(minutes=15)

                if break_start and break_end:
                    break_start_dt = datetime.combine(selected_date, break_start)
                    break_end_dt = datetime.combine(selected_date, break_end)
                    if break_start_dt <= current_time < break_end_dt:
                        current_time = slot_end
                        continue

                if not Appointment.objects.filter(
                    deputy=self.deputy,
                    appointed_date=selected_date,
                    appointed_time=current_time.time(),
                    is_archived=False
                ).exists():
                    time_slots.append((
                        current_time.strftime('%H:%M'),
                        current_time.strftime('%H:%M')
                    ))

                current_time = slot_end

        return time_slots

    def clean(self):
        cleaned_data = super().clean()
        appointed_date = cleaned_data.get('appointed_date')
        appointed_time = cleaned_data.get('appointed_time')

        if appointed_date and appointed_time:
            appointed_datetime = timezone.make_aware(
                datetime.combine(appointed_date, appointed_time)
            )
            if appointed_datetime <= timezone.now():
                raise forms.ValidationError("Нельзя записаться на прошедшую дату или время.")
        return cleaned_data

# class AppointmentForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         deputy_id = kwargs.pop('deputy_id', None)
#         super().__init__(*args, **kwargs)
        
#         if deputy_id:
#             today = timezone.now().date()
#             slots = DeputySchedule.get_available_slots(deputy_id, today)
#             print(f"ДОСТУПНЫЕ СЛОТЫ: {slots}")
            
#             # Преобразуем слоты в choices для Select
#             self.fields['appointed_date'].widget = forms.Select(
#                 choices=[(f"{today} {slot}", slot.strftime('%H:%M')) for slot in slots],
#                 attrs={'class': 'form-control'}
#             )
    
#     class Meta:
#         model = Appointment
#         fields = ['title', 'appointment_theme', 'description', 'appointed_date']
#         widgets = {
#             'appointed_date': forms.HiddenInput() 
#         }


class MoveAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointed_date', 'appointed_time']
        widgets = {
            'appointed_date': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_appointed_date'
            }),
            'appointed_time': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_appointed_time'
            }),
        }
        labels = {
            'appointed_date': 'Дата записи',
            'appointed_time': 'Время записи',
        }

    def __init__(self, *args, deputy=None, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        if deputy:
            self.deputy = deputy
            available_dates = self.get_available_dates()
            self.fields['appointed_date'].widget.choices = [('', 'Выберите дату')] + available_dates
            self.fields['appointed_time'].widget.choices = [('', 'Сначала выберите дату')]
            if instance:
                self.fields['appointed_date'].initial = instance.appointed_date
                self.fields['appointed_time'].initial = instance.appointed_time

    def get_available_dates(self):
        if not self.deputy:
            return []

        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        available_dates = set()

        schedules = DeputySchedule.objects.filter(deputy=self.deputy, is_available=True)
        for schedule in schedules:
            day_of_week = schedule.day_of_week
            for i in range(1, 31):
                target_date = tomorrow + timedelta(days=i)
                if target_date.weekday() + 1 == day_of_week:
                    available_dates.add((
                        target_date.strftime('%Y-%m-%d'),
                        target_date.strftime('%d.%m.%Y')
                    ))

        return sorted(list(available_dates), key=lambda x: x[0])

    def clean(self):
        cleaned_data = super().clean()
        appointed_date = cleaned_data.get('appointed_date')
        appointed_time = cleaned_data.get('appointed_time')

        if appointed_date and appointed_time:
            appointed_datetime = timezone.make_aware(
                datetime.combine(appointed_date, appointed_time)
            )
            if appointed_datetime <= timezone.now():
                raise forms.ValidationError("Нельзя перенести запись на прошедшую дату или время.")
        return cleaned_data
    

class EmailConfirmationForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    code = forms.CharField(
        label='Код подтверждения',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите код из письма'})
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.code_sent = False
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        code = cleaned_data.get('code')
        
        if email and self.user.email != email:

            if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
                raise forms.ValidationError({
                    'email': 'Этот email уже используется другим пользователем'
                })
            
            if not code:
                try:
                    confirmation = EmailConfirmation.create_confirmation(self.user, email)
                    self.code_sent = True

                    raise forms.ValidationError({
                        'code_required': 'На указанный email отправлен код подтверждения'
                    })
                except Exception as e:
                    raise forms.ValidationError({
                        'email': f'Ошибка отправки кода: {str(e)}'
                    })
            
            try:
                confirmation = EmailConfirmation.objects.get(
                    user=self.user,
                    email=email,
                    code=code,
                    is_confirmed=False,
                    created_at__gte=timezone.now() - timezone.timedelta(hours=24)
                )
                confirmation.is_confirmed = True
                confirmation.save()
            except EmailConfirmation.DoesNotExist:
                raise forms.ValidationError({
                    'code': 'Неверный код подтверждения'
                })
        
        return cleaned_data
    
class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['receive_notifications']
        widgets = {
            'receive_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class StatusChangeForm(forms.Form):
    update_reason = forms.CharField(
        label="Причина изменения",
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Укажите причину изменения статуса (необязательно)'
        })
    )


class EditDecisionForm(forms.ModelForm):
    class Meta:
        model = Decision
        fields = ['decision_text']
        widgets = {
            'decision_text': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Напишите Ваше решение'

            }),
        }

class DecisionForm(forms.ModelForm):
    class Meta:
        model = Decision
        fields = ['decision_text', 'is_final']
        widgets = {
            'decision_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Опишите ваше решение'
            }),
            'is_final': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'decision_text': 'Текст решения',
            'is_final': 'Окончательное решение?',
        }

    def __init__(self, *args, appointment=None, deputy=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.appointment = appointment
        self.deputy = deputy