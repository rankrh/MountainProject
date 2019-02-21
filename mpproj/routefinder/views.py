from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from .models import Route


def index(request):
    return HttpResponse('This is the routes page')

def search(request):
    # Ordered list of route difficulties in human readable format. Used for sport,
    # trad, and tr routes.  Only Yosemite Decimal System (YDS) is supported right
    # now.
    rope_conv = [
        '3rd', '4th', 'Easy 5th', '5.0', '5.1', '5.2', '5.3', '5.4', '5.5',
        '5.6', '5.7', '5.7+', '5.8-', '5.8', '5.8+', '5.9-', '5.9', '5.9+',
        '5.10a', '5.10-', '5.10a/b', '5.10b', '5.10', '5.10b/c', '5.10c',
        '5.10+', '5.10c/d', '5.10d', '5.11a', '5.11-', '5.11a/b', '5.11b',
        '5.11', '5.11b/c', '5.11c', '5.11+', '5.11c/d', '5.11d', '5.12a',
        '5.12-', '5.12a/b', '5.12b', '5.12', '5.12b/c', '5.12c', '5.12+',
        '5.12c/d', '5.12d', '5.13a', '5.13-', '5.13a/b', '5.13b', '5.13',
        '5.13b/c', '5.13c', '5.13+', '5.13c/d', '5.13d', '5.14a', '5.14-',
        '5.14a/b', '5.14b', '5.14', '5.14b/c', '5.14c', '5.14+', '5.14c/d',
        '5.14d', '5.15a', '5.15-', '5.15a/b', '5.15b', '5.15', '5.15c',
        '5.15+', '5.15c/d', '5.15d']

    # Ordered list of route difficulties in human readable format. Used for
    # bouldering routes. Only Hueco rating system is supported
    boulder_conv  = [
        'V-easy', 'V0-', 'V0', 'V0+', 'V0-1', 'V1-', 'V1', 'V1+', 'V1-2',
        'V2-', 'V2', 'V2+', 'V2-3', 'V3-', 'V3', 'V3+', 'V3-4', 'V4-', 'V4',
        'V4+', 'V4-5', 'V5-', 'V5', 'V5+', 'V5-6', 'V6-', 'V6', 'V6+', 'V6-7',
        'V7-', 'V7', 'V7+', 'V7-8', 'V8-', 'V8', 'V8+', 'V8-9', 'V9-', 'V9',
        'V9+', 'V9-10', 'V10-', 'V10', 'V10+', 'V10-11', 'V11-', 'V11', 'V11+',
        'V11-12', 'V12-', 'V12', 'V12+', 'V12-13', 'V13-', 'V13', 'V13+',
        'V13-14', 'V14-', 'V14', 'V14+', 'V14-15', 'V15-', 'V15', 'V15+',
        'V15-16', 'V16-', 'V16', 'V16+', 'V16-17', 'V17-', 'V17']

    # Ordered list of route difficulties in human readable format.  Used for mixed
    # routes.
    mixed_conv = [
        'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11',
        'M12']

    # Ordered list of route difficulties in human readable format. Used for Aid
    # routes
    aid_conv = ['A0', 'A1', 'A2', 'A2+', 'A3', 'A3+', 'A4', 'A4+', 'A5','A6']
    # Ordered list of route difficulties in human readable format. Used for snow
    # routes.
    snow_conv = ['Easy', 'Mod', 'Steep']
    # Ordered list of route difficulties in human readable format. Used for ice
    # routes.
    ice_conv = [
        '1', '1+', '1-2', '2', '2+', '2-3', '3', '3+', '3-4', '4','4+', '4-5',
        '5', '5+', '5-6', '6', '6+', '6-7', '7', '7+', '7-8', '8']

    climb_type_to_grade = {
        'sport': rope_conv,
        'trad': rope_conv,
        'tr': rope_conv,
        'boulder': boulder_conv,
        'mixed': mixed_conv,
        'aid': aid_conv,
        'ice': ice_conv,
        'snow': snow_conv}

    context = {
        'styles': climb_type_to_grade,
    }
    return render(request, 'routefinder/search.html', context)

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
