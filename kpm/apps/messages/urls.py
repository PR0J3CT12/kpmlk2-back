from django.urls import path
from . import views

urlpatterns = [
    path('send-message', views.send_message, name='send message'),
    path('get-message', views.get_message, name='get message'),
    path('get-messages', views.get_messages, name='get messages'),
    path('get-sent-messages', views.get_sent_messages, name='get sent messages'),
    path('delete-messages', views.delete_message, name='delete messages'),
    path('read-message', views.read_message, name='read message'),
    path('support', views.support, name='support'),
]
