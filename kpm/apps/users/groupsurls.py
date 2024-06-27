from django.urls import path
from . import views

urlpatterns = [
    path('create-group', views.create_group, name='create group'),
    path('get-groups', views.get_groups, name='get groups'),
    path('delete-group', views.delete_group, name='delete group'),
    path('add-to-group', views.add_to_group, name='add to group'),
    path('delete-from-group', views.delete_from_group, name='delete user from group'),
]
