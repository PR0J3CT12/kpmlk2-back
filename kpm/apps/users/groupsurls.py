from django.urls import path
from . import views

urlpatterns = [
    path('create-group', views.create_group, name='create group'),
    path('get-groups', views.get_groups, name='get groups'),
    path('get-group', views.get_group, name='get group'),
    path('delete-group', views.delete_group, name='delete group'),
    path('update-group', views.update_group, name='update group'),
    path('add-to-group', views.add_to_group, name='add to group'),
    path('delete-from-group', views.delete_from_group, name='delete user from group'),
]
