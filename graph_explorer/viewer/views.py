from django.http import JsonResponse
from django.shortcuts import render
from project_platform.core import GraphPlatform

def index(request):
    """Main page"""
    return render(request, 'index.html', {'message': 'Radi. Ovo je samo test prikaz.'})

def list_plugins(request):
    # Ovo treba da dobiješ iz platforme
    plugins = GraphPlatform().get_data_source_plugins()
    
    return JsonResponse(plugins, safe=False)  # safe=False dozvoljava listu umesto dict