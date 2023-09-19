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
    path('group/create-group', views.create_group, name='create group'),
    path('group/get-groups', views.get_groups, name='get groups'),
    path('group/delete-group', views.delete_group, name='delete group'),
    path('group/add-to-group', views.add_to_group, name='add to group'),
    path('group/delete-from-group', views.delete_from_group, name='delete from group'),
]
