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
    path('api/visualizer-assets/', views.visualizer_assets, name='visualizer_assets'),
    path('api/graph-operations/', views.apply_graph_operations, name='graph_operations'),
    path('api/workspaces/', views.list_workspaces, name='workspaces'),
    path('api/workspaces/create/', views.create_workspace, name='create_workspace'),
    path('api/workspaces/save/', views.save_workspace, name='save_workspace'),
    path('api/workspaces/switch/', views.switch_workspace, name='switch_workspace'),
    path('api/workspaces/delete/', views.delete_workspace, name='delete_workspace'),
]
