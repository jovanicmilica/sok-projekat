from django.urls import path
from . import views

app_name = 'viewer'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/plugins/', views.list_plugins, name='list_plugins'),
    path('api/plugins/<str:plugin_name>/parameters/', views.get_data_plugin_parameters, name='plugin_parameters')
]
