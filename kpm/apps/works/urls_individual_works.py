from django.urls import path
from kpm.apps.works import views_individual_works as views

urlpatterns = [
    path('get-all-individual-works', views.get_all_individual_works, name='get all individual works'),
]
