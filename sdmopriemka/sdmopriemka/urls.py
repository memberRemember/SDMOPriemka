from django.contrib import admin
from django.urls import path, re_path, include

from priemka.views import *

urlpatterns = [
    path('admin/', admin.site.urls, name='django_admin'),
    path('', include('priemka.urls')),
    path('priemka/', include('priemka.urls')),

]
