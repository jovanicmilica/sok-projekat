from django.urls import path
from . import views

app_name = 'viewer'

urlpatterns = [
    path('', views.index, name='index'),
    path('graph-data/', views.graph_data, name='graph_data'),
    path('render-graph/', views.render_graph, name='render_graph'),
    path('api/plugins/', views.list_plugins, name='list_plugins'),
    path('api/plugins/<str:plugin_name>/parameters/',
         views.get_data_plugin_parameters, name='plugin_parameters'),
    path('api/load-graph/', views.load_graph, name='load_graph'),
    path('api/visualizers/', views.list_visualizers, name='list_visualizers'),
]
