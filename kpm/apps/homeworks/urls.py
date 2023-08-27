from django.urls import path
from . import views

urlpatterns = [
    path('create-homework', views.create_homework, name='create homework'),
    path('delete-homework', views.delete_homework, name='delete homework'),
]
