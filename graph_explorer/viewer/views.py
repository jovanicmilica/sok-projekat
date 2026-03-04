from django.http import JsonResponse
from django.shortcuts import render
from project_platform.core import GraphPlatform
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

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

@csrf_exempt
@require_http_methods(["POST"])
def load_graph(request):
    try:
        data = json.loads(request.body)
        
        data_source = data.get('plugin')
        visualizer = data.get('visualizer', 'simple-view')
        parameters = data.get('parameters', {})
        
        platform = GraphPlatform()
        
        graph = platform.load_graph(
            data_source_plugin_name=data_source,
            visualizer_plugin_name=visualizer,
            **parameters
        )
        
        node_count = len(graph.nodes) if graph and hasattr(graph, 'nodes') else 0
        edge_count = len(graph.edges) if graph and hasattr(graph, 'edges') else 0
                
        return JsonResponse({
            'status': 'success',
            'message': f'Graph loaded with {data_source}',
            'visualizer': visualizer,
            'node_count': node_count,
            'edge_count': edge_count
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()  
        return JsonResponse({'error': str(e)}, status=500)
    
def list_visualizers(request):
    platform = GraphPlatform()
    visualizers = platform.get_visualizer_plugins()
    return JsonResponse(visualizers, safe=False)

    