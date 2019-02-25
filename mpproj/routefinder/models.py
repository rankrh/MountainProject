import numpy as np
from django.db import models
from django.http import Http404
import pandas as pd
from .StyleInformation import *
from config import config
from sqlalchemy import create_engine
from googlemaps.haversine import Haversine
from googlemaps.geocode import GeoCode


user = config.config()['user']
host = config.config()['host']
password = config.config()['password']
database = config.config()['database']

connection = f'postgresql://{user}:{password}@{host}:5432/{database}'
engine = create_engine(connection)

def get_counts(area_group):
    """Counts the number of similar routes in an area.

    Area groups were calculated after the data was gathered, and are used here
    to group similar routes.  Route difficulty, type, and style are all taken
    into account, so the counts cannot be calculated until the user defines
    their preferences.

    Args:
        area_group(Pandas Dataframe): Grouped by area group ID given by the
            MPAnalyzer script

    Returns:
        area_group(Pandas Dataframe): Dataframe with new column 'area_counts'
            that holds the number of routes in the area group
    """
    # An area_group ID of -1 means there are no other routes in the area
    if area_group.name == -1:
        area_group['area_counts'] = 1
    else:
        area_group['area_counts'] = len(area_group)

    return area_group


class Route(models.Model):
    name = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    bayes = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    trad = models.BooleanField(blank=True, null=True)
    tr = models.BooleanField(blank=True, null=True)
    sport = models.BooleanField(blank=True, null=True)
    aid = models.BooleanField(blank=True, null=True)
    snow = models.BooleanField(blank=True, null=True)
    ice = models.BooleanField(blank=True, null=True)
    mixed = models.BooleanField(blank=True, null=True)
    boulder = models.BooleanField(blank=True, null=True)
    alpine = models.BooleanField(blank=True, null=True)
    pitches = models.FloatField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    nccs_conv = models.FloatField(blank=True, null=True)
    boulder_conv = models.FloatField(blank=True, null=True)
    rope_conv = models.FloatField(blank=True, null=True)
    ice_conv = models.FloatField(blank=True, null=True)
    snow_conv = models.FloatField(blank=True, null=True)
    aid_conv = models.FloatField(blank=True, null=True)
    mixed_conv = models.FloatField(blank=True, null=True)
    danger_conv = models.FloatField(blank=True, null=True)
    area_id = models.FloatField(blank=True, null=True)
    area_group = models.FloatField(blank=True, null=True)
    arete = models.FloatField(blank=True, null=True)
    chimney = models.FloatField(blank=True, null=True)
    crack = models.FloatField(blank=True, null=True)
    slab = models.FloatField(blank=True, null=True)
    overhang = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Routes_scored'

    def __str__(self):
        return self.name

    def get_terrain_types(self):
        terrain = pd.Series([
            self.arete,
            self.chimney,
            self.slab,
            self.overhang,
            self.crack],
            index=terrain_types
        )

        terrain = pd.Series([
            int(round(self.arete, 1) * 100),
            int(round(self.chimney, 1) * 100),
            int(round(self.slab, 1) * 100),
            int(round(self.overhang, 1) * 100),
            int(round(self.crack, 1) * 100)],
            index=terrain_types)

        most_likely_terrain = terrain.max()
        most_likely_terrain =  terrain[terrain == most_likely_terrain]

        terrain = terrain[terrain > 50]
        terrain = terrain.sort_values(ascending=False)
        if len(terrain) > 0:
            return terrain.to_dict()
        else:
            return most_likely_terrain.to_dict()

    def other_routes_in_area(self):
        other_routes = Route.objects.filter(area_id=self.area_id)
        other_routes = other_routes.exclude(name=self.name)
        if len(other_routes) == 0:
            return None
        other_routes = other_routes.order_by('-bayes')  

        return other_routes

    def similar_routes_nearby(self):
        if self.area_group == -1:
            return
        
        route_information = {
            'sport': {
                'search': self.sport,
                'grade': self.rope_conv},
            'trad': {
                'search': self.trad,
                'grade': self.rope_conv},
            'tr': {
                'search': self.tr,
                'grade': self.rope_conv},
            'boulder': {
                'search': self.boulder,
                'grade': self.boulder_conv},
            'mixed': {
                'search': self.mixed,
                'grade': self.mixed_conv},
            'snow': {
                'search': self.snow,
                'grade': self.snow_conv},
            'aid': {
                'search': self.aid,
                'grade': self.aid_conv},
            'ice': {
                'search': self.ice,
                'grade': self.ice_conv},
            'alpine': {
                'search': self.alpine,
                'grade': self.nccs_conv}}

        filters = {'area_group': self.area_group}

        for style, data in route_information.items():
            filters[style] = data['search']
            if data['search']:
                filters[style] = data['search']
                filters[climb_style_to_system[style] + "__lte"] = data['grade'] + 3
                filters[climb_style_to_system[style] + "__gte"] = data['grade'] - 3


        other_routes = Route.objects.filter(**filters)
        other_routes = other_routes.exclude(name=self.name)
        other_routes = other_routes.order_by('-bayes')

        return other_routes

    def best_routes(get_request):

        if len(get_request) == 0:
            return

        for key, value in get_request.items():
            value = value[0]
            if value.isdigit():
                value = int(value)
            elif value == '':
                value = None
            elif value == "True":
                value = True
            elif value == "False":
                value = False
            elif key == "location":
                # Returns tuple of coordinates
                location_name = value
                value = GeoCode(value)
            elif value not in terrain_types:
                raise Http404

            get_request[key] = value

        try:
            pitch_min = get_request['pitch_min']
        except KeyError:
            pitch_min = 0

        try:
            pitch_max = get_request['pitch_max']
        except KeyError:
            pitch_max = 10

        try:
            user_location = get_request['location']
        except KeyError:
            user_location = None

        try:
            distance_max = get_request['distance']
        except KeyError:
            distance_max = 500

        try:
            terrain_type = get_request['terrain_type']
        except KeyError:
            terrain_type = None

        try:
            danger = int(get_request['danger'])
        except KeyError:
            danger = 100
        except ValueError:
            return Http404

        try:
            commitment = int(get_request["commitment"])
        except KeyError:
            commitment = 100
        except ValueError:
            return Http404

        ignore = []

        query = 'SELECT * FROM "Routes_scored"'
        joiner = ' WHERE'
        for style in climbing_styles:
            if style in get_request:
                query += f'{joiner} ({style} is TRUE'

                try:
                    grade_min = int(get_request[style+'_min'])
                except KeyError:
                    grade_min = 0
                try:
                    grade_max = int(get_request[style+'_max'])
                except KeyError:
                    grade_max = 100
                grade_system = climb_style_to_system[style]

                query += f' AND {grade_system} BETWEEN {grade_min} AND {grade_max}'

                if style in multipitch_styles:
                    # If the high end is below 10, finds routes between the low
                    # and high, inclusive.
                    if pitch_max < 10:
                        query += f' AND pitches BETWEEN {pitch_min} AND {pitch_max}'
                    # If the high end is 10, finds routes that are at least the
                    # low end
                    elif pitch_max == 10:
                        query += f' AND pitches >= {pitch_min}'                    
                    
                query += ') '

                joiner = ' OR'

            else:
                ignore.append(style)

        if query != 'SELECT * FROM "Routes_scored"':
            for style in ignore:
                query += f' AND {style} IS FALSE'
            try:
                query += f' AND danger_conv <= {danger}'
                query += f' AND nccs_conv <= {commitment}'
    
            except ValueError:
                raise Http404

            if user_location is None:
                query += ' AND area_counts >= 20'
                query += ' ORDER BY bayes LIMIT 1000'


        else:
            query += ' WHERE bayes > 3.0'
            query += ' AND area_counts >= 20 LIMIT 100'
            query += ' LIMIT 100'

        routes = pd.read_sql(query, con=engine)

        if terrain_type is not None:
            routes = routes[routes[terrain_type] >= 0.5]
            if len(routes) == 0:
                return

        if user_location is not None:
            routes['distance'] = Haversine(
                user_location,
                (routes['latitude'], routes['longitude']))

            if distance_max is not None:
                routes = routes[routes['distance'] <= distance_max]
            else:
                routes = routes[routes['distance'] <= 500]

            if len(routes) == 0:
                return None
        else:
            routes['distance'] = 1
        
        routes = routes.groupby('area_group').apply(get_counts)

        # Calculates the value of the routes.  Highly rated routes should be
        # more heavily weighted than lower rated ones, and the number of
        # routes in an area should affect the final rating in a diminishing
        # way.  Distance should be punished more as it gets further from the
        # user.
        routes['value'] = (
            ((routes['bayes'] ** 2) * (np.log(routes['area_counts']) + np.e))
            / (routes['distance'] ** 3))

        terrain = ['arete', 'chimney', 'crack', 'slab', 'overhang']
        feats = np.where(routes[terrain].gt(0.51, 0), terrain, None)
        feats = pd.DataFrame(feats, index=routes.index)
        feats = feats.apply(
                lambda x: ', '.join(x.dropna()), axis=1)

        routes['features'] = feats

        for style, system in climbing_systems.items():
            routes[style] = routes[style].map(pd.Series(system))

        # Collapses different grading systems into one column
        routes['grade'] = routes[list(climbing_systems.keys())].apply(
            lambda x: ', '.join(x.dropna()), axis=1)

        for style in climbing_styles:
            routes[style] = np.where(routes[style], style, None)

        routes['style'] = routes[climbing_styles].apply(
            lambda x: ', '.join(x.dropna()), axis=1
        )
        # Selects the top ten routes
        routes = routes.sort_values(by='value', ascending=False)
        display_columns = ['id', 'name', 'bayes', 'grade', 'features', 'style', 'pitches', 'length', 'url']
        routes = routes[display_columns]

        routes = routes.to_dict(orient='records')

        return routes