from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Route
from .models import Area
from .StyleInformation import *
import os


def browse(request):
    context = {}
    return render(request, 'routefinder/browse.html', context)

def area(request, area_id):
    area_data = get_object_or_404(Area, pk=area_id)

    context = {
        'area': area_data,
        'parent': area_data.parent_areas(),
        'children': area_data.children_areas(),
        'features': area_data.terrain(),
        'styles': area_data.styles(),
        'grades': area_data.grades(),
    }

    return render(request, 'routefinder/area.html', context)


def route(request, route_id):
    route_data = get_object_or_404(Route, pk=route_id)

    context = {
        'route': route_data,
        'terrain': route_data.format_terrain(),
        'terrain_val': {
            'arete': max(route_data.arete, 0.15),
            'chimney': max(route_data.chimney, 0.15),
            'crack': max(route_data.crack, 0.15),
            'slab': max(route_data.slab, 0.15),
            'overhang': max(route_data.overhang, 0.15)
            },
        'areas': route_data.area(),
        'area_routes': route_data.other_routes_in_area(),
        'similar_routes': route_data.similar_routes_nearby(),
        'styles': route_data.route_style(),
        'grades': route_data.route_grade(),
        'sport_systems': ['YDS', 'French', 'Ewbank', 'UIAA', 'South Africa', 'British'],
        'boulder_systems': ['Hueco', 'Fontaine Bleu'],
        'GOOGLE_KEY': os.environ.get('GOOGLE_API_KEY'),
    }
    return render(request, 'routefinder/route.html', context)


def results(request):

    best_routes = Route.best_routes(dict(request.GET))

    context = {
        'best_routes': best_routes,
    }

    return render(request, 'routefinder/results.html', context)


def search(request):
    context = {
        'styles': climb_style_to_grade,
        'pitch_count': [p for p in range(11)],
        'danger_levels': ['G', 'PG13', 'R', 'All Danger Levels'],
        'commitment_levels':['I', 'II', 'III', 'IV', 'All Commitment Levels'],
        'terrain_types': ['arete', 'crack', 'chimney', 'slab', 'overhang'],
        'GOOGLE_KEY': os.environ.get('GOOGLE_API_KEY'),}
    return render(request, 'routefinder/index.html', context)

