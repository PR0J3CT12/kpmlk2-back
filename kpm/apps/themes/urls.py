from django.urls import path
from . import views

urlpatterns = [
    path('get-theme', views.get_theme, name='get theme'),
    path('get-all-themes', views.get_themes, name='get all themes'),
    path('create-theme', views.create_theme, name='create theme'),
    path('delete-theme', views.delete_theme, name='delete theme'),
    path('delete-all-themes', views.delete_themes, name='delete all themes'),
]
