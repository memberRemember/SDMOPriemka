from django.contrib import admin
from django.conf.urls import include
from django.urls import *
from django.contrib.auth.views import LogoutView
import priemka.views as v


urlpatterns = [
    path('test/', v.test_email, name='test_email'),
    path('admin/', v.admin_index, name='admin_index_page'),
    path('', v.priemka_index, name='priemka_index_page'),
    path('cabinet/appointments', v.priemka_lc_appointments, name='priemka_lc_appointments_page'),
    path('cabinet/appointments_manage', v.priemka_lc_appointments_manage, name='priemka_lc_appointments_manage_page'),
    path('cabinet/appointments_deputy', v.priemka_lc_appointments_deputy, name='priemka_lc_appointments_deputy_page'),
    path('cabinet/appointments_today_deputy/', v.priemka_lc_appointments_today_deputy, name='priemka_lc_appointments_today_deputy_page'),
    path('cabinet/decisions', v.priemka_lc_decisions, name='priemka_lc_decisions_page'),
    path('cabinet/decisions_deputy', v.priemka_lc_decisions_deputy, name='priemka_lc_decisions_deputy_page'),
    path('cabinet/decisions/<int:decision_id>', v.decision_details, name='priemka_lc_decisions_details_page'),
    path('cabinet/deputy_profile', v.priemka_lc_deputy_profile, name='priemka_lc_deputy_profile_page'),
    path('cabinet/appointments/<int:appointment_id>', v.appointment_details, name='priemka_appointment_details_page'),
    path('cabinet/settings', v.priemka_lc_settings, name='priemka_lc_settings_page'),
    path('cabinet/chats', v.priemka_lc_chats, name='priemka_lc_chats_page'),
    path('cabinet/decision/create/<int:appointment_id>/', v.decision_creation, name='create_decision'),
    path('cabinet/statistics', v.priemka_lc_statistics, name='priemka_lc_statistics_page'),
    
    path('deputy/<int:deputy_id>/appointment/', v.create_appointment, name='create_appointment'),
    path('deputy/<int:deputy_id>/time-slots/', v.get_time_slots, name='get_time_slots'),
    path('appointment/success/', v.appointment_success, name='appointment_success'),

    path('confirm-email/', v.EmailConfirmationView.as_view(), name='email_confirmation'),
    path('registration/', v.RegisterUser.as_view(), name='registration'),
    path('login/', v.AuthUser.as_view(), name='authuser'),
    path('userlogout/', v.CustomLogoutPriemkaView.as_view(), name='userlogout'),


    path('chat/start/', v.start_chat, name='start_chat'),
    path('chat/send/', v.send_message, name='send_message'),
    path('chat/get/', v.get_messages, name='get_messages'),
    path('chat/mark_read/', v.mark_secretary_messages_read, name='mark_secretary_messages_read'),

    path('cabinet/chats/<int:chat_id>/', v.chat_detail, name='chat_detail'),
    path('cabinet/chats/<int:chat_id>/send/', v.send_chat_message, name='send_chat_message'),
    path('cabinet/chats/<int:chat_id>/close/', v.close_chat, name='close_chat'),
    path('cabinet/chats/<int:chat_id>/reopen/', v.reopen_chat, name='reopen_chat'),
    path('cabinet/chats/<int:chat_id>/messages/', v.get_chat_messages, name='get_chat_messages'),
    path('cabinet/chats/<int:chat_id>/mark_read/', v.mark_user_messages_read, name='mark_user_messages_read'),

]