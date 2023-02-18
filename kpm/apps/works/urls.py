from django.urls import path
from . import views

urlpatterns = [
    path('get-all', views.get_works, name='get all works'),
    path('get-all/theme-sorted', views.get_works_sorted_by_theme, name='get all works which sorted by theme'),
    path('get', views.get_some_works, name='get some works'),
    path('create', views.create_work, name='create work'),
    path('update', views.update_work, name='update work'),
    path('delete', views.delete_work, name='delete work'),
    path('delete-all', views.delete_works, name='delete all works'),
    path('get-ids', views.get_works_id, name='get works id'),
    path('grades-update', views.update_work_grades, name='update work grades'),
]
