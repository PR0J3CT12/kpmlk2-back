from django.urls import path
from . import views

urlpatterns = [
    path('get-stats', views.get_stats, name='get stats'),
    path('get-graph', views.get_graph, name='get graph'),
]
