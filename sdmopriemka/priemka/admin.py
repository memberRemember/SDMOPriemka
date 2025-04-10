from django.contrib import admin
from .models import *

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('rolename',)
    search_fields = ('rolename',)

@admin.register(ElectoralDistrict)
class ElectoralDistrictAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(AppointmentTheme)
class AppointmentThemeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(AppointmentStatus)
class AppointmentStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(DecisionStatus)
class DecisionStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('login', 'last_name', 'first_name', 'email', 'rolename', 'is_active', 'join_date')
    search_fields = ('login', 'last_name', 'first_name', 'email')
    list_filter = ('is_active', 'role')

    def rolename(self, obj):
        return obj.role.rolename
    rolename.short_description = 'Role'

@admin.register(Deputy)
class DeputyAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'patronymic_name', 'position', 'district_name', 'email')
    search_fields = ('last_name', 'first_name', 'patronymic_name', 'position', 'email')
    list_filter = ('electoral_district',)

    def district_name(self, obj):
        return obj.electoral_district.name
    district_name.short_description = 'Electoral District'

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('deputy_name', 'user_name', 'title', 'appointment_theme', 'status_name', 'appointed_date', 'appointed_time', 'is_archived', 'creation_date')
    search_fields = ('title', 'deputy__last_name', 'user__last_name')
    list_filter = ('appointment_status', 'is_archived', 'appointment_theme')

    def deputy_name(self, obj):
        return obj.deputy.get_full_name()
    deputy_name.short_description = 'Депутат'

    def user_name(self, obj):
        return obj.user.get_full_name()
    user_name.short_description = 'Посетитель'

    def theme_name(self, obj):
        return obj.appointment_theme.name
    theme_name.short_description = 'Тема'

    def status_name(self, obj):
        return obj.appointment_status.name
    status_name.short_description = 'Статус'

@admin.register(Decision)
class DecisionAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'deputy_name', 'decision_text', 'status_name', 'created_at', 'updated_at', 'is_final', 'is_archived')
    search_fields = ('appointment', 'deputy_name', 'decision_text', 'status_name','is_final',)
    list_filter = ('status', 'is_archived', 'is_final',)

    def deputy_name(self, obj):
        return obj.deputy.get_full_name()
    deputy_name.short_description = 'Deputy'


    def status_name(self, obj):
        return obj.status.name
    status_name.short_description = 'Status'

@admin.register(DeputySchedule)
class DeputyScheduleAdmin(admin.ModelAdmin):
    list_display = ('deputy_name', 'day_of_week', 'start_time', 'end_time', 'is_available',)
    search_fields = ('deputy__last_name',)
    list_filter = ('is_available', 'day_of_week')

    def deputy_name(self, obj):
        return obj.deputy.get_full_name()
    deputy_name.short_description = 'Deputy'

@admin.register(EmailConfirmation)
class EmailConfirmationAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'email', 'code', 'created_at', 'is_confirmed',)
    search_fields = ('user_name','email','code','is_confirmed')
    list_filter = ('is_confirmed',)

    def user_name(self, obj):
        return obj.user.get_full_name()
    user_name.short_description = 'User'


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'secretary_name', 'created_at', 'is_active',)
    search_fields = ('user_name','secretary_name','created_at','is_active')
    list_filter = ('is_active',)

    def user_name(self, obj):
        return obj.user.get_full_name()
    
    def secretary_name(self, obj):
        return obj.secretary.get_full_name()
    
    user_name.short_description = 'User'
    secretary_name.short_description = 'Secretary'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender_name', 'text', 'timestamp','is_read')
    search_fields = ('chat','sender_name','text','timestamp','is_read')
    list_filter = ('is_read',)

    def sender_name(self, obj):
        return obj.sender.get_full_name()
    
    sender_name.short_description = 'Sender'
