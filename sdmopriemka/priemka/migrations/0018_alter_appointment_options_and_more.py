# Generated by Django 4.2.20 on 2025-04-05 16:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import pgtrigger.compiler
import pgtrigger.migrations


class Migration(migrations.Migration):

    dependencies = [
        ('priemka', '0017_decisionstatus_decision_decision_appointment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='appointment',
            options={'verbose_name': 'Запись на прием', 'verbose_name_plural': 'Записи на прием'},
        ),
        migrations.AlterModelOptions(
            name='appointmentstatus',
            options={'verbose_name': 'Статус приема', 'verbose_name_plural': 'Статусы приема'},
        ),
        migrations.AlterModelOptions(
            name='appointmenttheme',
            options={'verbose_name': 'Тема приема', 'verbose_name_plural': 'Темы приема'},
        ),
        migrations.AlterModelOptions(
            name='chat',
            options={'verbose_name': 'Чат', 'verbose_name_plural': 'Чаты'},
        ),
        migrations.AlterModelOptions(
            name='deputy',
            options={'verbose_name': 'Депутат', 'verbose_name_plural': 'Депутаты'},
        ),
        migrations.AlterModelOptions(
            name='deputyschedule',
            options={'verbose_name': 'Расписание депутата', 'verbose_name_plural': 'Расписания депутатов'},
        ),
        migrations.AlterModelOptions(
            name='electoraldistrict',
            options={'verbose_name': 'Избирательный округ', 'verbose_name_plural': 'Избирательные округа'},
        ),
        migrations.AlterModelOptions(
            name='emailconfirmation',
            options={'verbose_name': 'Подтверждение email', 'verbose_name_plural': 'Подтверждения email'},
        ),
        migrations.AlterModelOptions(
            name='message',
            options={'verbose_name': 'Сообщение', 'verbose_name_plural': 'Сообщения'},
        ),
        migrations.AlterModelOptions(
            name='role',
            options={'verbose_name': 'Роль', 'verbose_name_plural': 'Роли'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        pgtrigger.migrations.RemoveTrigger(
            model_name='decision',
            name='appointment',
        ),
        migrations.AlterField(
            model_name='appointment',
            name='appointed_date',
            field=models.DateField(verbose_name='Дата приема'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='appointed_time',
            field=models.TimeField(default='08:30', verbose_name='Время приема'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='appointment_status',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='priemka.appointmentstatus', verbose_name='Статус приема'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='appointment_theme',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='priemka.appointmenttheme', verbose_name='Тема приема'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='creation_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='deputy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='priemka.deputy', verbose_name='Депутат'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='description',
            field=models.TextField(null=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='is_archived',
            field=models.BooleanField(blank=True, default=False, verbose_name='Архивировано'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='title',
            field=models.CharField(max_length=50, verbose_name='Заголовок'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='appointmentstatus',
            name='name',
            field=models.CharField(db_index=True, max_length=50, unique=True, verbose_name='Название статуса'),
        ),
        migrations.AlterField(
            model_name='appointmenttheme',
            name='name',
            field=models.CharField(db_index=True, max_length=255, unique=True, verbose_name='Название темы'),
        ),
        migrations.AlterField(
            model_name='chat',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='chat',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активен'),
        ),
        migrations.AlterField(
            model_name='chat',
            name='secretary',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='secretary_chats', to=settings.AUTH_USER_MODEL, verbose_name='Секретарь'),
        ),
        migrations.AlterField(
            model_name='chat',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_chats', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='decision',
            name='is_archived',
            field=models.BooleanField(blank=True, default=False, verbose_name='Архивировано'),
        ),
        migrations.AlterField(
            model_name='decisionstatus',
            name='name',
            field=models.CharField(db_index=True, max_length=50, unique=True, verbose_name='Название статуса'),
        ),
        migrations.AlterField(
            model_name='deputy',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='deputy',
            name='electoral_district',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='priemka.electoraldistrict', verbose_name='Избирательный округ'),
        ),
        migrations.AlterField(
            model_name='deputy',
            name='email',
            field=models.EmailField(blank=True, max_length=50, null=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='deputy',
            name='first_name',
            field=models.CharField(blank=True, max_length=50, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='deputy',
            name='image',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='deputy',
            name='last_name',
            field=models.CharField(blank=True, max_length=50, verbose_name='Фамилия'),
        ),
        migrations.AlterField(
            model_name='deputy',
            name='patronymic_name',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Отчество'),
        ),
        migrations.AlterField(
            model_name='deputy',
            name='position',
            field=models.CharField(blank=True, max_length=255, verbose_name='Должность'),
        ),
        migrations.AlterField(
            model_name='deputy',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='deputyschedule',
            name='break_end',
            field=models.TimeField(blank=True, null=True, verbose_name='Окончание перерыва'),
        ),
        migrations.AlterField(
            model_name='deputyschedule',
            name='break_start',
            field=models.TimeField(blank=True, null=True, verbose_name='Начало перерыва'),
        ),
        migrations.AlterField(
            model_name='deputyschedule',
            name='day_of_week',
            field=models.IntegerField(choices=[(1, 'Понедельник'), (2, 'Вторник'), (3, 'Среда'), (4, 'Четверг'), (5, 'Пятница'), (6, 'Суббота'), (7, 'Воскресенье')], verbose_name='День недели'),
        ),
        migrations.AlterField(
            model_name='deputyschedule',
            name='deputy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='priemka.deputy', verbose_name='Депутат'),
        ),
        migrations.AlterField(
            model_name='deputyschedule',
            name='end_time',
            field=models.TimeField(verbose_name='Время окончания'),
        ),
        migrations.AlterField(
            model_name='deputyschedule',
            name='is_available',
            field=models.BooleanField(blank=True, default=False, verbose_name='Доступен'),
        ),
        migrations.AlterField(
            model_name='deputyschedule',
            name='start_time',
            field=models.TimeField(verbose_name='Время начала'),
        ),
        migrations.AlterField(
            model_name='electoraldistrict',
            name='name',
            field=models.CharField(db_index=True, max_length=255, unique=True, verbose_name='Название округа'),
        ),
        migrations.AlterField(
            model_name='emailconfirmation',
            name='code',
            field=models.CharField(max_length=6, verbose_name='Код подтверждения'),
        ),
        migrations.AlterField(
            model_name='emailconfirmation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='emailconfirmation',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='emailconfirmation',
            name='is_confirmed',
            field=models.BooleanField(default=False, verbose_name='Подтверждено'),
        ),
        migrations.AlterField(
            model_name='emailconfirmation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='message',
            name='chat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='priemka.chat', verbose_name='Чат'),
        ),
        migrations.AlterField(
            model_name='message',
            name='is_read',
            field=models.BooleanField(default=False, verbose_name='Прочитано'),
        ),
        migrations.AlterField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Отправитель'),
        ),
        migrations.AlterField(
            model_name='message',
            name='text',
            field=models.TextField(verbose_name='Текст сообщения'),
        ),
        migrations.AlterField(
            model_name='message',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Время отправки'),
        ),
        migrations.AlterField(
            model_name='role',
            name='rolename',
            field=models.CharField(db_index=True, max_length=25, unique=True, verbose_name='Название роли'),
        ),
        migrations.AlterField(
            model_name='user',
            name='creation_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=50, null=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=50, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активен'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False, verbose_name='Сотрудник'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_superuser',
            field=models.BooleanField(default=False, verbose_name='Суперпользователь'),
        ),
        migrations.AlterField(
            model_name='user',
            name='join_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата регистрации'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=50, verbose_name='Фамилия'),
        ),
        migrations.AlterField(
            model_name='user',
            name='login',
            field=models.CharField(max_length=25, unique=True, verbose_name='Логин'),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=255, verbose_name='Пароль'),
        ),
        migrations.AlterField(
            model_name='user',
            name='patronymic_name',
            field=models.CharField(blank=True, default=' ', max_length=50, null=True, verbose_name='Отчество'),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.ForeignKey(blank=True, default=0, on_delete=django.db.models.deletion.PROTECT, to='priemka.role', verbose_name='Роль'),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name='decision',
            trigger=pgtrigger.compiler.Trigger(name='decision', sql=pgtrigger.compiler.UpsertTriggerSql(func='UPDATE "priemka_decision" SET is_archived = True WHERE "id" = OLD."id"; RETURN NULL;', hash='ad9919d161eb3c881ab8713ea4122b9ee1dd2aa2', operation='DELETE', pgid='pgtrigger_decision_20424', table='priemka_decision', when='BEFORE')),
        ),
    ]
