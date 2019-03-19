from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.core.exceptions import *
from .models import Results
from .models import Route
from .models import Area
from .models import AreaLinks
from .models import TerrainTypes
from .models import StyleTypes
from .StyleInformation import *
from .forms import SortMethod
import os
import pandas as pd


def search(request):
    context = {
        'rope_grades': yds_rating,
        'boulder_grades': hueco_rating,
        'mixed_grades': mixed_rating,
        'aid_grades': aid_rating,
        'snow_grades': snow_rating,
        'ice_grades': ice_rating,
        'pitch_count': [p for p in range(11)],
        'danger_levels': ['G', 'PG13', 'R', 'All Danger Levels'],
        'commitment_levels':['I', 'II', 'III', 'IV', 'All Commitment Levels'],
        'terrain_types': ['arete', 'crack', 'chimney', 'slab', 'overhang']}
    return render(request, 'routefinder/index.html', context)


def results(request):

    get_request = Results.parse_get_request(request.GET)

    context = {
        'results': Results.best_routes(get_request),
        'location': get_request['location']
    }

    return render(request, 'routefinder/results.html', context)


def browse(request):

    return render(request, 'routefinder/browse.html', {})


def location(request):
    base_areas = Area.objects.filter(from_id=None).order_by('id')

    areas = []

    for area in base_areas:
        sub_areas = Area.objects.filter(from_id=area.id).order_by('id')
        areas.append({area: sub_areas})

    context = {
        'areas': areas}
    return render(request, 'routefinder/location.html', context)


def style(request):

    return render(request, 'routefinder/style.html', {})


def terrain(request):

    return render(request, 'routefinder/terrain.html', {})


def terrain_style(request, terrain_type):

    if terrain_type not in terrain_types:
        raise Http404
    
    routes = TerrainTypes.get_routes(terrain_type)

    parents = [get_object_or_404(Route, pk=route.id).areas() for route in routes]

    routes = [(routes[i], parents[i]) for i in range(len(routes))]
    context = {
        'terrain': terrain_type,
        'routes': routes,
    }

    return render(request, 'routefinder/terrain_style.html', context)


def terrain_areas(request, terrain_type):
    if terrain_type not in terrain_types:
        raise Http404
    
    areas = TerrainTypes.get_areas(terrain_type)

    area_objects = [get_object_or_404(Area, pk=area.id) for area in areas]
    parents = [area.parents() for area in area_objects]
    styles = [area.styles() for area in area_objects]
    grades = [area.grade_avg() for area in area_objects]

    areas = [(areas[i], parents[i][:-1], styles[i], grades[i]) for i in range(len(areas))]

    context = {
        'terrain': terrain_type,
        'areas': areas,
    }

    return render(request, 'routefinder/terrain_areas.html', context)


def area(request, area_id):
    area_data = get_object_or_404(Area, pk=area_id)

    if area_data is not None:
        pitches = area_data.pitches
        if pitches is not None:
            pitches = round(pitches)

        length = area_data.length
        if length is not None:
            length = round(length)
        
        rating = area_data.bayes
        if rating is not None:
            rating = round(rating, 1)

        context = {
            'area': area_data,
            'parent': area_data.parents(),
            'children': area_data.children(),
            'classics': area_data.classics(),
            'terrain': area_data.terrain(),
            'styles': area_data.styles(),
            'grade_avg': area_data.grade_avg(),
            'grade_std': area_data.grade_std(),
            'rating': rating,
            'commitment': area_data.alpine_rating,
            'pitches': pitches,
            'length': length,
        }
    else:
        context = {
            'area': area_data,
            'parent': area_data.parents(),
            'children': area_data.children(),
            'terrain': area_terrain,
            'styles': None,
            'rating': '?',
        }


    return render(request, 'routefinder/area.html', context)


def route(request, route_id):
    route_data = get_object_or_404(Route, pk=route_id)

    context = {
        'route': route_data,
        'parent': route_data.areas(),
        'area_routes': route_data.area_routes(),
        'similar_routes': route_data.similar_routes(),
        'terrain': route_data.terrain(),
        'styles': route_data.styles(),
        'rope_grades': route_data.rope_grades(),
        'boulder_grades': route_data.boulder_grades(),
        'other_grades': route_data.other_grades(),
    }
    return render(request, 'routefinder/route.html', context)


def climbing_style(request, climbing_style):

    if climbing_style not in climbing_styles + ['alpine', 'all']:
        raise Http404
    
    routes = StyleTypes.get_routes(climbing_style)

    parents = [get_object_or_404(Route, pk=route.id).areas() for route in routes]

    routes = [(routes[i], parents[i]) for i in range(len(routes))]

    context = {
        'style': climbing_style,
        'routes': routes,
    }
    return render(request, 'routefinder/climbing_style.html', context)


def area_style(request, climbing_style):


    if climbing_style not in climbing_styles:
        raise Http404
    
    areas = StyleTypes.get_areas(climbing_style)

    area_objects = [get_object_or_404(Area, pk=area.id) for area in areas]
    parents = [area.parents() for area in area_objects]
    styles = [area.styles() for area in area_objects]
    grades = [area.grade_avg() for area in area_objects]

    areas = [(areas[i], parents[i][:-1], styles[i], grades[i]) for i in range(len(areas))]

    context = {
        'areas': areas,
        'style': climbing_style,
    }
    return render(request, 'routefinder/area_style.html', context)

