from django.urls import path
from . import views

urlpatterns = [
    path('get-all', views.get_mana_waiters, name='get all mana waiters'),
    path('give', views.give_mana_all, name='give mana'),
    path('stats', views.get_mana_stats, name='get mana stats'),
]
