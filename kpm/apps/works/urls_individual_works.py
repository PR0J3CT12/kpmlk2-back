from django.urls import path
from kpm.apps.works import views_individual_works as views

urlpatterns = [
    path('get-all-individual-works', views.get_all_individual_works, name='get all individual works'),
    path('get-my-individual-works', views.get_my_individual_works, name='get my individual works'),
    path('check-user-individual-work', views.check_user_individual_work, name='check user individual work'),
    path('create-response-individuals', views.create_response, name='create response on individual work'),
    path('get-user-individual-work', views.get_user_individual_work, name='get user individual work'),
    path('add-to-individual-work', views.add_to_individual_work, name='add to individual work'),
    path('delete-from-individual-work', views.delete_from_individual_work, name='delete user from individual work'),
    path('return-individual-work', views.return_user_individual_work, name='return individual work'),
    path('set-individual-work-dates', views.set_individual_work_date, name='set individual work date'),
    path('delete-individual-work-dates', views.delete_individual_work_dates, name='delete homework dates'),
    path('get-individual-works-dates', views.get_individual_works_dates, name='get homeworks dates'),
    path('get-all-answers-individuals', views.get_all_answers_individuals, name='get all answers individuals'),
]
