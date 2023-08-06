from django.urls import path
from . import views

urlpatterns = [
    path('insert', views.insert_grades, name='insert grades'),
    path('get', views.get_grades, name='get grades in order'),
    path('mana/get-all', views.get_mana_waiters, name='get all mana waiters'),
    #path('mana/get', views.get_some_mana_waiters, name='get some mana waiters'),
    #path('mana/give-some', views.give_mana, name='give mana'),
    path('mana/give', views.give_mana_all, name='give mana'),
]
