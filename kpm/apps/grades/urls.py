from django.urls import path
from . import views

urlpatterns = [
    path('insert', views.insert_grades, name='insert grades'),
    path('get', views.get_grades, name='get grades in order'),
]
