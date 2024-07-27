from django.urls import path
from . import views

urlpatterns = [
    path('get-my-homeworks', views.get_my_homeworks, name='get user homeworks'),
    path('check-user-homework', views.check_user_homework, name='check user homework'),
    path('create-response', views.create_response, name='create response on homework'),
    path('get-user-work', views.get_user_work, name='get user homework'),
    path('add-to-homework', views.add_to_work, name='add to homework'),
    path('delete-from-homework', views.delete_from_work, name='delete user from work'),
    path('set-homework-dates', views.set_homeworks_dates, name='set homework dates')
]
