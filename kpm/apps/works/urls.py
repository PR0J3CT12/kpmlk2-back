from django.urls import path
from . import views

urlpatterns = [
    path('get-all-works', views.get_works, name='get all works'),
    path('get-work', views.get_work, name='get work'),
    path('create-work', views.create_work, name='create work'),
    path('update-work', views.update_work, name='update work'),
    path('delete-work', views.delete_work, name='delete work'),
    path('delete-all-works', views.delete_works, name='delete all works'),
    path('get-my-homeworks', views.get_my_homeworks, name='get user homeworks'),
    path('check-user-homework', views.check_user_homework, name='check user homework'),
    path('create-response', views.create_response, name='create response on homework'),
    path('check-homework', views.check_user_homework, name='check user homework'),
    path('get-user-work', views.get_user_work, name='get user homework'),
    path('add-to-homework', views.add_to_work, name='add to homework'),
    path('delete-from-work', views.delete_from_work, name='delete user from work'),
    path('delete-file', views.delete_file_from_work, name='delete file from work'),
]
