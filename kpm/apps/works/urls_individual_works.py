from django.urls import path
from . import views

urlpatterns = [
    path('get-all-individual-works', views.get_all_individual_works, name='get all individual works'),
]
