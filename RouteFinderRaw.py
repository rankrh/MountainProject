import sqlite3
import pandas as pd
from googlemaps.haversine import Haversine
from googlemaps.geocode import GeoCode
import numpy as np

conn = sqlite3.connect('Routes-Cleaned.sqlite')

grade_conv = {
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
            'grades': (68, 76),
            'system': 'yds_rating'}, 
        'trad': {
            'search': False,
            'slider_id': 'trad_slide',
            'label_id': 'trad_diff',
            'grades': (68, 76),
            'system': 'font_rating'},
        'tr': {
            'search': False,
            'slider_id': 'tr_slide',
            'label_id': 'tr_diff',
            'grades': (None, None),
            'system': 'yds_rating'},
        'boulder': {
            'search': False,
            'slider_id': 'boulder_slide',
            'label_id': 'boulder_diff',
            'grades': (23, 46),
            'system': 'hueco_rating'},
        'mixed': {
            'search': False,
            'slider_id': 'mixed_slide',
            'label_id': 'mixed_diff',
            'grades': (1, 8),
            'system': 'mixed_rating'},
        'snow': {
            'search': False,
            'slider_id': 'snow_slide',
            'label_id': 'snow_diff',
            'grades': (None, None),
            'system': 'snow_rating'},
        'aid': {
            'search': False,
            'slider_id': 'aid_slide',
            'label_id': 'aid_diff',
            'grades': (None, None),
            'system': 'aid_rating'},
        'ice': {
            'search': False,
            'slider_id': 'ice_slide',
            'label_id': 'ice_diff',
            'grades': (None, None),
            'system': 'aid_rating'}}
        
decode_systems = {
    'sport': 'uiaa_rating',
    'trad': 'za_rating',
    'tr': 'yds_rating',
    'boulder': 'hueco_rating',
    'ice': 'ice_rating',
    'snow': 'snow_rating',
    'aid': 'aid_rating',
    'mixed': 'mixed_rating'}


preferences = {
        'pitches': (0,11), 
        'danger': 3, 
        'commitment': 3,
        'location': {
            'name': 'Missoula',
            'coordinates': (None, None)},
        'distance': None,
        'features': {
            'arete': False,
            'chimney': False,
            'crack': False,
            'slab': False,
            'overhang': False}}
        
def get_counts(area_group):
    if area_group.name != -1:
        area_group['area_counts'] = len(area_group)
    else:
        area_group['area_counts'] = 1        
    return area_group

def get_max(table):
    return table
        
        
def route_finder(styles, preferences):
    query = 'SELECT * FROM Routes'
    
    search = []
    first = True
    ignore = []

    systems = []

    for style, data in styles.items():
        if data['search']:
            search.append(style)
            decoded = data['system']
            if decoded not in systems:
                systems.append(decoded)
        else:
            if style != 'tr':
                ignore.append(style)
            
    for style in search:
        if first:
            joiner = ' WHERE'
        else:
            joiner = ' OR'
        first = False

        
        grade_range = styles[style]['grades']
        conversion = grade_conv[style]
        keys = (conversion,) + grade_range
        grades = '%s BETWEEN %s AND %s' % keys

        pitches = ''        
        if style in multipitch_styles:
            pitch_range = preferences['pitches']
            if pitch_range[1] < 11:
                pitches = ' AND pitches BETWEEN %s AND %s' % pitch_range
            elif pitch_range[1] == 11:
                pitches = ' AND pitches >= %s' % pitch_range[0]
        keys = (joiner, style, grades, pitches)
        query += '%s (%s is 1 AND %s%s)' % (keys)
    
    if len(search) >= 1:
        for style in ignore:
            query += ' AND %s = 0' % style
        
    routes = pd.read_sql(query, con=conn, index_col='route_id')

    if len(routes) == 0:
        return 'No Routes'
    
    #danger = preferences['danger']
    #routes = routes[routes['danger_conv'].values <= danger]

    location = preferences['location']
    location_name = location['name']
    coordinates = location['coordinates']

    if location_name is not None:
        location['coordinates'] = GeoCode(location_name)
        
    if all(coordinates):
        routes['distance'] = Haversine(
            coordinates,
            (routes['latitude'], routes['longitude']))
        distance = preferences['distance']
        routes = routes[routes.distance < distance]

    else:
        routes['distance'] = 1
        


    if len(routes) == 0:
        return 'No Routes'

    features = preferences['features']            
    for feature, value in features.items():
        if value:
            routes = routes[routes[feature] > 0.95]

    if len(routes) == 0:
        return 'No Routes'

    routes = routes.groupby('area_group').apply(get_counts)
    
        
    routes['value'] = (
        (100 * routes['bayes'] * np.log(routes['area_counts'] + 0.001) + np.e)
        / (routes['distance'] ** 2))

    routes = routes.head(10).sort_values(by='value', ascending=False)
    routes.rename(columns={'name': 'Name'}, inplace=True)
    routes = routes.set_index('Name')
    routes['Rating'] = routes['bayes'].round(1)

    routes['Grade'] = routes[systems]
    
    terrain = ['arete', 'chimney', 'crack', 'slab', 'overhang']
    feats =  np.where(routes[terrain].gt(0.75, 0), terrain, '')
    routes['Features'] = pd.Series([' '.join(x).strip() for x in feats], index=routes.index)

#    routes[terrain] = routes[terrain].mask(routes[terrain] < 0.75)
    
    #feats = np.where(routes[terrain].gt(0.75, 0), terrain, None)
    #feats = pd.DataFrame(feats, index=routes.index)
    #feats = feats.apply(
    #        lambda x: ', '.join(x.dropna()), axis=1)
    
    routes['Features'] = feats

    display_columns = ['Rating', 'Grade', 'Features']

    return routes[display_columns]




print(route_finder(styles, preferences))    
    

