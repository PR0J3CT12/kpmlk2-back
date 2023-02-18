from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/user/', include('users.urls')),
    path('api/grade/', include('grades.urls')),
    path('api/log/', include('logs.urls')),
    path('api/session/', include('mysessions.urls')),
    path('api/theme/', include('themes.urls')),
    path('api/work/', include('works.urls')),
]
