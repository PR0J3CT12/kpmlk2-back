from django.urls import path
from . import views

urlpatterns = [
    path('get-all-works', views.get_works, name='get all works'),
    path('get-work', views.get_work, name='get work'),
    path('create-work', views.create_work, name='create work'),
    path('update-work', views.update_work, name='update work'),
    path('delete-work', views.delete_work, name='delete work'),
    path('delete-all-works', views.delete_works, name='delete all works'),
]
