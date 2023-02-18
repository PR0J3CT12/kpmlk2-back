from django.urls import path
from . import views

urlpatterns = [
    path('get', views.get_theme, name='get theme'),
    path('get-all', views.get_themes, name='get all themes'),
    path('create', views.create_theme, name='create theme'),
    path('delete', views.delete_theme, name='delete theme'),
    path('delete-all', views.delete_themes, name='delete all themes'),
]
