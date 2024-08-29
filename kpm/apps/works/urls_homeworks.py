from django.urls import path
from kpm.apps.works import views_homeworks as views

urlpatterns = [
    path('get-my-homeworks', views.get_my_homeworks, name='get user homeworks'),
    path('get-all-homeworks', views.get_all_homeworks, name='get all homeworks'),
    path('check-user-homework', views.check_user_homework, name='check user homework'),
    path('create-response', views.create_response, name='create response on homework'),
    path('get-user-homework', views.get_user_homework, name='get user homework'),
    path('add-to-homework', views.add_to_homework, name='add to homework'),
    path('delete-from-homework', views.delete_from_homework, name='delete user from homework'),
    path('set-homework-dates', views.set_homework_date, name='set homework date'),
    path('delete-homework-dates', views.delete_homework_dates, name='delete homework dates'),
    path('get-homeworks-dates', views.get_homeworks_dates, name='get homeworks dates'),
    path('return-homework', views.return_user_homework, name='get return homework'),
    path('get-all-answers', views.get_all_answers, name='get all answers'),
]
