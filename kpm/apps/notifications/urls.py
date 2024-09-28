from django.urls import path
from . import views

urlpatterns = [
    path('get-notifications', views.get_notifications, name='get notifications'),
]
