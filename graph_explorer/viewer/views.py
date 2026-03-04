from django.http import JsonResponse
from django.shortcuts import render
from project_platform.core import GraphPlatform

def index(request):
    """Main page"""
    return render(request, 'index.html', {'message': 'Radi. Ovo je samo test prikaz.'})

def list_plugins(request):
    # getting all plugin names from the GraphPlatform 
    plugins = GraphPlatform().get_data_source_plugins()
    return JsonResponse(plugins, safe=False)  # safe=False allows us to return a list instead of a dict

def get_data_plugin_parameters(request, plugin_name):
    """
    API endpoint koji vraća parametre za dati plugin.
    GET /api/plugins/<plugin_name>/parameters/
    """
    platform = GraphPlatform()
    try:
        parameters = platform.get_data_source_plugin_parameters(plugin_name)
        return JsonResponse(parameters, safe=False)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)