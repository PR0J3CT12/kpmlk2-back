from django.urls import path
from . import views

urlpatterns = [
    path('get-ratings', views.get_ratings, name='get ratings'),
    path('create-rating', views.create_rating, name='create rating'),
    path('delete-rating', views.delete_rating, name='delete rating'),
    path('delete-from-rating', views.delete_from_rating, name='delete from rating'),
    path('add-to-rating', views.add_to_rating, name='add to rating'),
    path('get-user-rating', views.get_user_rating, name='get user rating'),
]