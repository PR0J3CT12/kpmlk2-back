from django.urls import path
from . import views

urlpatterns = [
    path('get-all', views.get_users, name='get users'),
    path('get', views.get_user, name='get user'),
    path('create', views.create_user, name='create user'),
    path('delete', views.delete_user, name='delete user'),
    path('delete-all', views.delete_users, name='delete all users'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('change-password', views.change_password, name='change password'),
    path('get-all-logons', views.get_all_logons, name='get all logons'),
    path('enable', views.enable_user, name='enable user'),
    path('disable', views.disable_user, name='disable user'),
]
