import sqlite3
import pandas as pd
from googlemaps.haversine import Haversine
from googlemaps.geocode import GeoCode
import numpy as np

conn = sqlite3.connect('Routes-Cleaned.sqlite')

grades = {
    'sport': 'rope_conv', 
    'trad': 'rope_conv',
    'tr': 'rope_conv',
    'boulder': 'boulder_conv',
    'mixed': 'mixed_conv',
    'snow': 'snow_conv',
    'aid': 'aid_conv',
    'ice': 'ice_conv',
    'alpine': 'nccs_conv'}

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

boulder_conv  = [
    'V-easy', 'V0-', 'V0', 'V0+', 'V0-1', 'V1-', 'V1', 'V1+', 'V1-2',
    'V2-', 'V2', 'V2+', 'V2-3', 'V3-', 'V3', 'V3+', 'V3-4', 'V4-', 'V4',
    'V4+', 'V4-5', 'V5-', 'V5', 'V5+', 'V5-6', 'V6-', 'V6', 'V6+', 'V6-7',
    'V7-', 'V7', 'V7+', 'V7-8', 'V8-', 'V8', 'V8+', 'V8-9', 'V9-', 'V9',
    'V9+', 'V9-10', 'V10-', 'V10', 'V10+', 'V10-11', 'V11-', 'V11', 'V11+',
    'V11-12', 'V12-', 'V12', 'V12+', 'V12-13', 'V13-', 'V13', 'V13+',
    'V13-14', 'V14-', 'V14', 'V14+', 'V14-15', 'V15-', 'V15', 'V15+',
    'V15-16', 'V16-', 'V16', 'V16+', 'V16-17', 'V17-', 'V17']

mixed_conv = [
    'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11',
    'M12']

aid_conv = ['A0', 'A1', 'A2', 'A2+', 'A3', 'A3+', 'A4', 'A4+', 'A5','A6']
ice_conv = [
    '1', '1+', '1-2', '2', '2+', '2-3', '3', '3+', '3-4', '4','4+', '4-5', '5',
    '5+', '5-6', '6', '6+', '6-7', '7', '7+', '7-8', '8']
snow_conv = ['Easy', 'Mod', 'Steep']

multipitch_styles = [
    'sport', 'trad', 'aid', 'mixed', 'alpine', 'snow', 'ice']


styles = {
        'sport': {
            'search': True,
            'slider_id': 'sport_slide',
            'label_id': 'sport_diff',
            'grades': (1, 32)}, 
        'trad': {
            'search': False,
            'slider_id': 'trad_slide',
            'label_id': 'trad_diff',
            'grades': (None, None)},
        'tr': {
            'search': False,
            'slider_id': 'tr_slide',
            'label_id': 'tr_diff',
            'grades': (None, None)},
        'boulder': {
            'search': False,
            'slider_id': 'boulder_slide',
            'label_id': 'boulder_diff',
            'grades': (4, 7)},
        'mixed': {
            'search': False,
            'slider_id': 'mixed_slide',
            'label_id': 'mixed_diff',
            'grades': (None, None)},
        'snow': {
            'search': False,
            'slider_id': 'snow_slide',
            'label_id': 'snow_diff',
            'grades': (None, None)},
        'aid': {
            'search': False,
            'slider_id': 'aid_slide',
            'label_id': 'aid_diff',
            'grades': (None, None)},
        'ice': {
            'search': False,
            'slider_id': 'ice_slide',
            'label_id': 'ice_diff',
            'grades': (None, None)}}


preferences = {
        'pitches': (4, 10), 
        'danger': 3, 
        'commitment': 3,
        'location': {
            'name': 'Missoula, MT',
            'coordinates': (None, None)},
        'distance': 300,
        'features': {
            'arete': False,
            'chimney': False,
            'crack': False,
            'slab': True,
            'overhang': False}}
        
def get_counts(area_group):
    if area_group.name != -1:
        area_group['area_counts'] = len(area_group)
    else:
        area_group['area_counts'] = 1        
    return area_group
        
        
def route_finder(styles, preferences):
    pitch_range = preferences['pitches']

    query = 'SELECT * FROM Routes'
    
    at_least_1 = False
    
    for style, data in styles.items():
        if data['search']:
            if not at_least_1:
                joiner = 'WHERE'
            else:
                joiner = 'OR'

            if style in multipitch_styles and all(pitch_range):  
                if pitch_range[1] < 11:
                    pitches = ' AND pitches BETWEEN %s AND %s' % pitch_range
                elif pitch_range[1] == 11:
                    pitches = ' AND pitches > %s' % pitch_range[0]
                    
            else:
                pitches = ''    
                
            low_grade = data['grades'][0]
            high_grade = data['grades'][1]
            conv = grades[style]
            
            keys = (joiner, style, conv, low_grade, high_grade, pitches)
            query += ' %s (%s = 1 AND %s BETWEEN %s AND %s%s)' % keys
            at_least_1 = True
        elif not data['search'] and style != 'tr':
            query += ' AND %s = 0' % style
    
    if not at_least_1:
        query = 'SELECT * FROM Routes'
        
    routes = pd.read_sql(query, con=conn, index_col='route_id')

    if len(routes) == 0:
        return 'No Routes'

    location = preferences['location']
    location_name = location['name']
    if location_name is not None:
        location['coordinates'] = GeoCode(location_name)
        coordinates = location['coordinates']
        
    if all(coordinates):
        routes['distance'] = Haversine(
            coordinates,
            (routes['latitude'], routes['longitude']))
    else:
        routes['distance'] = 1
        
    distance = preferences['distance']
    if distance:
        routes = routes[routes.distance < distance]

    if len(routes) == 0:
        return 'No Routes'

    features = preferences['features']            
    for feature, value in features.items():
        if value:
            routes = routes[routes[feature] > 0.75]
            print(feature)

    if len(routes) == 0:
        return 'No Routes'

    routes = routes.groupby('area_group').apply(get_counts)
    
        
    routes['raw'] = (
        (100 * routes['bayes'] * np.log(routes['area_counts'] + 0.001) + np.e)
        / (routes['distance'] ** 2))
    


    routes = routes[['name', 'raw', 'bayes', 'distance', 'area_counts', 'slab']]

    pd.options.display.max_rows = len(routes)
    pd.options.display.max_columns = (len(routes.columns))
    routes = routes.sort_values(by='raw', ascending=False)
    
    return routes




print(route_finder(styles, preferences))    
    

