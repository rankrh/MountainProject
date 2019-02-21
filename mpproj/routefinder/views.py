from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from .models import Route


def index(request):
    return HttpResponse('This is the routes page')

def search(request):
    return HttpResponse('This is the search page')

def results(request):
    return HttpResponse('This is the results page')

def route(request, route_id):
    route_name = get_object_or_404(Route, pk=route_id)
    context = {
        'route_name': route_name,
        'terrain': route_name.terrain_types(),
        'url': route_name.url,
        'area_routes': route_name.other_routes_in_area(),
        'similar_routes': route_name.similar_routes_nearby(),
    }
    return render(request, 'routefinder/route.html', context)
