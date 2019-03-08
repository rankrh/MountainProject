from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Results
from .models import Route
from .models import Area
from .models import AreaTerrain
from .models import AreaGrades
from .models import AreaLinks
from .StyleInformation import *
from .forms import SortMethod
import os
import pandas as pd


def browse(request):
    context = {}
    return render(request, 'routefinder/browse.html', context)

def area(request, area_id):
    area_data = get_object_or_404(Area, pk=area_id)

    context = {
        'area': area_data,
        'parent': area_data.parents(),
        'children': area_data.children(),
        'terrain': get_object_or_404(AreaTerrain, pk=area_id),
        'styles': get_object_or_404(AreaGrades, pk=area_id)
    }

    return render(request, 'routefinder/area.html', context)


def route(request, route_id):
    route_data = get_object_or_404(Route, pk=route_id)

    context = {
        'route': route_data,
        'areas': route_data.areas(),
        'area_routes': route_data.area_routes(),
        'similar_routes': route_data.similar_routes(),
        'terrain': route_data.terrain(),
        'styles': route_data.styles(),
        'rope_grades': route_data.rope_grades(),
        'boulder_grades': route_data.boulder_grades(),
        'other_grades': route_data.other_grades(),
    }
    return render(request, 'routefinder/route.html', context)


def results(request):

    get_request = Results.parse_get_request(request.GET)
    try:
        sort = get_request['sort']
    except:
        sort = 'value'

    best_routes = Results.best_routes(get_request, sort=sort)

    user_location = get_request['location']
    if user_location is '':
        user_location = None

    context = {
        'user_location': user_location,
        'best_routes': best_routes,
        'form': SortMethod(),
        'get_request': request.GET,
    }

    return render(request, 'routefinder/results.html', context)


def search(request):
    context = {
        'rope_grades': rope_conv,
        'boulder_grades': boulder_conv,
        'mixxed_grades': mixed_conv,
        'aid_grades': aid_conv,
        'snow_grades': snow_conv,
        'ice_grades': ice_conv,
        'pitch_count': [p for p in range(11)],
        'danger_levels': ['G', 'PG13', 'R', 'All Danger Levels'],
        'commitment_levels':['I', 'II', 'III', 'IV', 'All Commitment Levels'],
        'terrain_types': ['arete', 'crack', 'chimney', 'slab', 'overhang']}
    return render(request, 'routefinder/index.html', context)

