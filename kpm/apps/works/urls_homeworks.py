from django.urls import path
from . import views

urlpatterns = [
    path('get-my-homeworks', views.get_my_homeworks, name='get user homeworks'),
    path('get-all-homeworks', views.get_homeworks, name='get all homeworks'),
    path('check-user-homework', views.check_user_homework, name='check user homework'),
    path('create-response', views.create_response, name='create response on homework'),
    path('get-user-homework', views.get_user_work, name='get user homework'),
    path('add-to-homework', views.add_to_work, name='add to homework'),
    path('delete-from-homework', views.delete_from_work, name='delete user from work'),
    path('set-homework-dates', views.set_homework_date, name='set homework date'),
    path('delete-homework-dates', views.delete_homework_date, name='delete homework date'),
    path('get-homeworks-dates', views.get_homeworks_dates, name='get homeworks dates')
]
