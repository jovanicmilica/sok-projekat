from django.shortcuts import render
from django.http import JsonResponse


def index(request):
    """Main page with graph visualization interface"""
    return render(request, 'index.html')
