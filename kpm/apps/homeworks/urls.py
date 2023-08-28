from django.urls import path
from . import views

urlpatterns = [
    path('create-homework', views.create_homework, name='create homework'),
    path('delete-homework', views.delete_homework, name='delete homework'),
    path('get-homework', views.get_homework, name='get homework'),
    path('add-to-homework', views.add_to_homework, name='add to homework'),
    path('delete-from-homework', views.delete_from_homework, name='delete from homework'),
    path('check-homework', views.check_user_homework, name='check user homework'),
    path('create-response', views.create_response, name='create response on homework'),
    path('get-user-homework', views.get_user_homework, name='get user homework'),
    path('get-my-homeworks', views.get_my_homeworks, name='get user homeworks'),
    path('get-all-homeworks', views.get_my_homeworks, name='get all homeworks'),
    path('get-all-answers', views.get_all_answers, name='get all answers'),
]
