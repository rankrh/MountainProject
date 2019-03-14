from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.exceptions import *
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
    base_areas = Area.objects.filter(from_id=None).order_by('id')

    areas = []

    for area in base_areas:
        sub_areas = Area.objects.filter(from_id=area.id).order_by('id')
        areas.append({area: sub_areas})

    context = {
        'areas': areas}
    return render(request, 'routefinder/browse.html', context)


def area(request, area_id):
    area_data = get_object_or_404(Area, pk=area_id)
    try:
        area_terrain = AreaTerrain.objects.get(pk=area_id)
    except ObjectDoesNotExist:
        area_terrain = {
            'arete': 0.15,
            'chimney': 0.15,
            'crack': 0.15,
            'slab': 0.15,
            'overhang': 0.15
        }
    try:
        area_styles = AreaGrades.objects.get(pk=area_id)
    except ObjectDoesNotExist:
        area_styles = None


    if area_styles is not None:
        pitches = area_styles.pitches
        if pitches is not None:
            pitches = round(pitches)

        length = area_styles.length
        if length is not None:
            length = round(length)
        
        rating = area_styles.bayes
        if rating is not None:
            rating = round(rating, 1)

        context = {
            'area': area_data,
            'parent': area_data.parents(),
            'children': area_data.children(),
            'classics': area_data.classics(),
            'terrain': area_terrain,
            'styles': area_styles.styles(),
            'grade_avg': area_styles.grade_avg(),
            'grade_std': area_styles.grade_std(),
            'rating': rating,
            'commitment': area_styles.alpine_rating,
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


def results(request):

    get_request = Results.parse_get_request(request.GET)

    context = {
        'results': Results.best_routes(get_request),
        'location': get_request['location']
    }

    return render(request, 'routefinder/results.html', context)


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

