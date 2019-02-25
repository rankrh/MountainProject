from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Route
from .StyleInformation import *


def index(request):
    return HttpResponse('This is the home page')


def search(request):
    context = {
        'styles': climb_style_to_grade,
        'pitch_count': [p for p in range(10)] + ['10 or more'],
        'danger_levels': ['G', 'PG13', 'R', 'All Danger Levels'],
        'commitment_levels':['I', 'II', 'III', 'IV', 'All Commitment Levels'],
        'terrain_types': ['arete', 'crack', 'chimney', 'slab', 'overhang']}
    return render(request, 'routefinder/search.html', context)


def route(request, route_id):
    route_name = get_object_or_404(Route, pk=route_id)
    context = {
        'route_name': route_name,
        'terrain': route_name.get_terrain_types(),
        'url': route_name.url,
        'area_routes': route_name.other_routes_in_area(),
        'similar_routes': route_name.similar_routes_nearby(),
    }
    return render(request, 'routefinder/route.html', context)

def results(request):

    best_routes = Route.best_routes(dict(request.GET))


    context = {
        'best_routes': best_routes
    }

    return render(request, 'routefinder/results.html', context)