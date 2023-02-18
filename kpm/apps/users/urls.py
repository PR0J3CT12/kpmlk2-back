from django.urls import path
from . import views

urlpatterns = [
    path('get-all', views.get_users, name='get users'),
    path('get', views.get_user, name='get user'),
    path('create', views.create_user, name='create user'),
    path('delete', views.delete_user, name='delete user'),
    path('delete-all', views.delete_users, name='delete all users'),

]
