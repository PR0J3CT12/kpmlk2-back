from django.urls import path
from kpm.apps.works import views_classworks as views

urlpatterns = [
    path('get-my-classworks', views.get_my_classworks, name='get user classworks'),
    path('add-files-to-classworks', views.apply_files_to_classwork, name='add files to classworks'),
    path('delete-file-from-classwork', views.delete_file_from_classwork, name='delete file to classwork'),
    path('get-classwork-files', views.get_classwork_files, name='get classwork files'),
    path('get-all-classworks', views.get_classworks, name='get all classworks'),
    path('get-classwork-grades', views.get_classwork_grades, name='get classwork grades'),
]
