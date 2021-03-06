import numpy as np
from django.db import models
from django.http import Http404
import pandas as pd
from .StyleInformation import *
from config import config
from sqlalchemy import create_engine
from googlemaps.haversine import Haversine
from googlemaps.geocode import GeoCode
from django.shortcuts import get_object_or_404

user = config.config()['user']
host = config.config()['host']
password = config.config()['password']
database = config.config()['database']

connection = f'postgresql://{user}:{password}@{host}:5432/{database}'
engine = create_engine(connection) 


class Area(models.Model):
    id = models.FloatField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    url = models.TextField(unique=True, blank=True, null=True)
    from_id = models.IntegerField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    arete = models.FloatField(blank=True, null=True)
    chimney = models.FloatField(blank=True, null=True)
    slab = models.FloatField(blank=True, null=True)
    overhang = models.FloatField(blank=True, null=True)
    crack = models.FloatField(blank=True, null=True)
    arete_diff = models.FloatField(blank=True, null=True)
    chimney_diff = models.FloatField(blank=True, null=True)
    slab_diff = models.FloatField(blank=True, null=True)
    overhang_diff = models.FloatField(blank=True, null=True)
    crack_diff = models.FloatField(blank=True, null=True)
    aid = models.FloatField(blank=True, null=True)
    aid_conv = models.FloatField(blank=True, null=True)
    aid_conv_std = models.FloatField(blank=True, null=True)
    aid_rating = models.TextField(blank=True, null=True)
    aid_rating_std = models.TextField(blank=True, null=True)
    alpine = models.FloatField(blank=True, null=True)
    alpine_rating = models.TextField(blank=True, null=True)
    alpine_rating_std = models.TextField(blank=True, null=True)
    bayes = models.FloatField(blank=True, null=True)
    boulder = models.FloatField(blank=True, null=True)
    boulder_conv = models.FloatField(blank=True, null=True)
    boulder_conv_std = models.FloatField(blank=True, null=True)
    british_rating = models.TextField(blank=True, null=True)
    british_rating_std = models.TextField(blank=True, null=True)
    danger_conv = models.FloatField(blank=True, null=True)
    ewbanks_rating = models.TextField(blank=True, null=True)
    ewbanks_rating_std = models.TextField(blank=True, null=True)
    font_rating = models.TextField(blank=True, null=True)
    font_rating_std = models.TextField(blank=True, null=True)
    french_rating = models.TextField(blank=True, null=True)
    french_rating_std = models.TextField(blank=True, null=True)
    hueco_rating = models.TextField(blank=True, null=True)
    hueco_rating_std = models.TextField(blank=True, null=True)
    ice = models.FloatField(blank=True, null=True)
    ice_conv = models.FloatField(blank=True, null=True)
    ice_conv_std = models.FloatField(blank=True, null=True)
    ice_rating = models.TextField(blank=True, null=True)
    ice_rating_std = models.TextField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    mixed = models.FloatField(blank=True, null=True)
    mixed_conv = models.FloatField(blank=True, null=True)
    mixed_conv_std = models.FloatField(blank=True, null=True)
    mixed_rating = models.TextField(blank=True, null=True)
    mixed_rating_std = models.TextField(blank=True, null=True)
    nccs_conv = models.FloatField(blank=True, null=True)
    nccs_conv_std = models.FloatField(blank=True, null=True)
    pitches = models.FloatField(blank=True, null=True)
    rope_conv = models.FloatField(blank=True, null=True)
    rope_conv_std = models.FloatField(blank=True, null=True)
    snow = models.FloatField(blank=True, null=True)
    snow_conv = models.FloatField(blank=True, null=True)
    snow_conv_std = models.FloatField(blank=True, null=True)
    snow_rating = models.TextField(blank=True, null=True)
    snow_rating_std = models.TextField(blank=True, null=True)
    sport = models.FloatField(blank=True, null=True)
    tr = models.FloatField(blank=True, null=True)
    trad = models.FloatField(blank=True, null=True)
    uiaa_rating = models.TextField(blank=True, null=True)
    uiaa_rating_std = models.TextField(blank=True, null=True)
    yds_rating = models.TextField(blank=True, null=True)
    yds_rating_std = models.TextField(blank=True, null=True)
    za_rating = models.TextField(blank=True, null=True)
    za_rating_std = models.TextField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'areas'
        ordering = ['from_id']

    def __str__(self):
        return self.name

    def parents(self):
        parent_areas = []

        for area in AreaLinks.objects.filter(pk=self.id).order_by('from_id'):
            parent_areas.append(get_object_or_404(Area, pk=area.from_id))
        parent_areas.append(self)

        return parent_areas

    def children(self):
        level = 'Routes'
        children = Route.objects.filter(area_id=self.id)
        if len(children) == 0:
            children = Area.objects.filter(from_id=self.id)
            level = 'Areas'
        return children, level

    def classics(self, limit=12):

        routes = RouteLinks.objects.filter(area=self.id)
        routes = Route.objects.filter(
            id__in=routes,
            bayes__gte=2.5).order_by(
                '-bayes'
            )[:limit]
        
        return routes

    def get_top_styles(self):
        route_styles = pd.Series(
            [self.sport, self.trad, self.tr, self.boulder, self.aid, self.mixed, self.ice, self.snow, self.alpine],
            index=climbing_styles+['alpine']
        )
        return route_styles.sort_values(ascending=False)

    def styles(self):
        route_styles = self.get_top_styles()

        score = 0
        num_types = 0
        while score < 0.75:
            num_types += 1
            styles_to_sum = route_styles.iloc[:num_types]
            score = styles_to_sum.sum()
        route_styles = route_styles.iloc[:num_types]
        return route_styles

    def grade_avg(self):

        top_style = self.get_top_styles().idxmax()
        if top_style in ['sport', 'trad', 'tr']:
            area_avg = {}
            for system in rope_systems:
                area_avg[system] = getattr(self, system)
            top_style = 'rope'
        elif top_style is 'boulder':
            area_avg = {}
            for system in boulder_systems:
                area_avg[system] = getattr(self, system)
        else:
            area_avg = {top_style + '_rating': getattr(self, top_style + '_rating')} 
        return (top_style, area_avg)

    def grade_std(self):

        top_style = self.get_top_styles().idxmax()
        if top_style in ['sport', 'trad', 'tr']:
            area_avg = {}
            for system in rope_systems:
                area_avg[system] = getattr(self, system+'_std')
        elif top_style is 'boulder':
            area_avg = {}
            for system in boulder_systems:
                area_avg[system] = getattr(self, system+'_std')
        else:
            area_avg = {top_style + '_rating': getattr(self, top_style + '_rating_std')} 
        return area_avg

    def terrain(self):
        area_terrain = pd.Series(
            data = [self.arete, self.chimney, self.slab, self.overhang, self.crack],
            index = terrain_types)

        area_terrain[area_terrain < 0.15] = 0.15

        return area_terrain

class AreaLinks(models.Model):
    from_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'area_links'


class RouteLinks(models.Model):
    id = models.FloatField(primary_key=True)
    area = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'route_links'
        

class Route(models.Model):
    arete = models.FloatField(blank=True, null=True)
    chimney = models.FloatField(blank=True, null=True)
    crack = models.FloatField(blank=True, null=True)
    slab = models.FloatField(blank=True, null=True)
    overhang = models.FloatField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    stars = models.FloatField(blank=True, null=True)
    votes = models.FloatField(blank=True, null=True)
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
    nccs_rating = models.TextField(blank=True, null=True)
    nccs_conv = models.FloatField(blank=True, null=True)
    hueco_rating = models.TextField(blank=True, null=True)
    font_rating = models.TextField(blank=True, null=True)
    boulder_conv = models.FloatField(blank=True, null=True)
    yds_rating = models.TextField(blank=True, null=True)
    french_rating = models.TextField(blank=True, null=True)
    ewbanks_rating = models.TextField(blank=True, null=True)
    uiaa_rating = models.TextField(blank=True, null=True)
    za_rating = models.TextField(blank=True, null=True)
    british_rating = models.TextField(blank=True, null=True)
    rope_conv = models.FloatField(blank=True, null=True)
    ice_rating = models.TextField(blank=True, null=True)
    ice_conv = models.FloatField(blank=True, null=True)
    snow_rating = models.TextField(blank=True, null=True)
    snow_conv = models.FloatField(blank=True, null=True)
    aid_rating = models.TextField(blank=True, null=True)
    aid_conv = models.FloatField(blank=True, null=True)
    mixed_rating = models.TextField(blank=True, null=True)
    mixed_conv = models.FloatField(blank=True, null=True)
    danger_rating = models.TextField(blank=True, null=True)
    danger_conv = models.FloatField(blank=True, null=True)
    area_id = models.FloatField(blank=True, null=True)
    area_group = models.FloatField(blank=True, null=True)
    area_counts = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'routes_scored'

    def __str__(self):
        return self.name

    def areas(self):
        parents = []
        for area in RouteLinks.objects.filter(pk=self.id).order_by('area'):
            if area.area is not None:
                parents.append(get_object_or_404(Area, pk=area.area))
        return parents


    def area_routes(self):
        other_routes = Route.objects.filter(area_id=self.area_id)
        other_routes = other_routes.exclude(name=self.name)
        if len(other_routes) == 0:
            return None
        other_routes = other_routes.order_by('-bayes')  

        return other_routes

    def similar_routes(self):
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
                'grade': self.ice_conv}}

        filters = {'area_group': self.area_group}

        for style, data in route_information.items():
            filters[style] = data['search']
            if data['search'] and data['grade'] is not None:
                filters[style] = data['search']
                filters[climb_style_to_system[style] + "__lte"] = data['grade'] + 3
                filters[climb_style_to_system[style] + "__gte"] = data['grade'] - 3

        filters["nccs_conv__lte"] = self.nccs_conv
        filters["danger_conv__lte"] = self.danger_conv
        
        if self.pitches <= 1:
            filters["pitches__lte"] = 1
        else:
            filters["pitches__lte"] = self.pitches + 2
            filters["pitches__gte"] = max(self.pitches - 2, 2)

        other_routes = Route.objects.filter(**filters)
        other_routes = other_routes.exclude(name=self.name)
        if len(other_routes) == 0:
            return

        other_routes = other_routes.order_by('-bayes')


        return other_routes

    def styles(self):

        route_styles = pd.Series([
            self.sport,
            self.trad,
            self.tr,
            self.boulder,
            self.mixed,
            self.aid,
            self.snow,
            self.ice,
            self.alpine],
            index = climbing_styles + ['alpine'])

        route_styles = route_styles.rename(climbing_styles_formatted)
        route_styles = route_styles[route_styles == True].index

        return route_styles

    def rope_grades(self):
        grades = {
            'yds_rating': self.yds_rating,
            'french_rating': self.french_rating,
            'ewbanks_rating': self.ewbanks_rating,
            'uiaa_rating': self.uiaa_rating,
            'za_rating': self.za_rating,
            'british_rating': self.british_rating}
        return grades

    def boulder_grades(self):
        grades = {
            'hueco_rating': self.hueco_rating,
            'font_rating': self.font_rating}
        return grades

    def other_grades(self):
        grades = {
        'mixed_rating': self.mixed_rating,
        'aid_rating': self.aid_rating,
        'snow_rating': self.snow_rating,
        'ice_rating': self.ice_rating}

        return grades

    def terrain(self):

        terrain_scores = pd.DataFrame({
            'scores': [
                max(self.arete, .15),
                max(self.chimney, .15),
                max(self.slab, .15),
                max(self.overhang, .15),
                max(self.crack, .15),
            ],
            'message': ['Unknown'] * 5},
            index=terrain_types)

        if terrain_scores['scores'].sum() <= 0.75:
            return terrain_scores
        else:
            terrain_scores['message'].loc[terrain_scores['scores'].lt(0.25)] =  'Almost certainly no'
            terrain_scores['message'].loc[terrain_scores['scores'].between(0.25, 0.5)] =  'Probably no'
            terrain_scores['message'].loc[terrain_scores['scores'].between(0.5, 0.75)] =  'Probably'
            terrain_scores['message'].loc[terrain_scores['scores'].between(0.75, 0.95)] =  'Almost certainly'
            terrain_scores['message'].loc[terrain_scores['scores'].gt(0.95)] =  'Definitely'

        return terrain_scores


class Results(models.Model):
    def best_routes(get_request, sort='value'):
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

        def get_parent_areas(pk):

            
            parents =  get_object_or_404(Area, pk=pk)
            parents = parents.parents()
            return parents

        try:
            pitch_min = get_request['pitch-min']
        except KeyError:
            pitch_min = 0

        try:
            pitch_max = get_request['pitch-max']
        except KeyError:
            pitch_max = 10

        if pitch_min > pitch_max:
            return 

        try:
            user_location = get_request['location']
        except KeyError:
            user_location = None

        try:
            distance_max = get_request['distance']
        except KeyError:
            distance_max = 500

        try:
            terrain_type = get_request['terrain-type']
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

        query = 'SELECT * FROM routes_scored'
        joiner = ' WHERE'
        for style in climbing_styles:
            if style in get_request:
                query += f'{joiner} ({style} is TRUE'

                try:
                    grade_min = int(get_request[style+'-min'])
                except KeyError:
                    grade_min = 0
                try:
                    grade_max = int(get_request[style+'-max'])
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

        if query != 'SELECT * FROM routes_scored':
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
            ((routes['bayes'] ** 2) * routes['area_counts'])
            / (routes['distance'] ** 2))

        terrain = ['arete', 'chimney', 'crack', 'slab', 'overhang']
        feats = np.where(routes[terrain].gt(0.51, 0), terrain, None)
        feats = pd.DataFrame(feats, index=routes.index)
        feats = feats.apply(
                lambda x: '/'.join(x.dropna()), axis=1)

        routes['terrain'] = feats

        for style in climbing_styles:
            routes[style] = np.where(routes[style], style, None)

        routes['rope_grades'] = routes[rope_systems].to_dict(orient='records')
        routes['boulder_grades'] = routes[boulder_systems].to_dict(orient='records')

        routes['style'] = routes[climbing_styles].apply(
            lambda x: ', '.join(x.dropna()), axis=1)

        routes['area'] = routes['area_id'].apply(get_parent_areas)

        if sort == "area_group":
            routes['area_group'] = routes['area_group'] * routes['area_counts']

        routes = routes.sort_values(by=sort, ascending=sort_methods[sort])

        routes['area_counts'] = routes['area_counts'] - 1

        routes = routes.to_dict(orient='records')

        return routes
        
    def parse_get_request(get_request):
        get_request = dict(get_request)
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
            elif key == "sort":
                if value not in sort_methods:
                    value = 'value'
            elif value not in terrain_types:
                raise Http404
            get_request[key] = value

        return get_request
    
class TerrainTypes(models.Model):
    def get_areas(terrain_type, **filters):

        filters[terrain_type + '_diff__gte'] =  0.95
        areas = Area.objects.filter(**filters).order_by('-bayes')[:50]

        return areas
        
    def get_routes(terrain_type, **filters):

        filters[terrain_type + '__gte'] = 0.95
        filters['bayes__gte'] = 3.0
        routes = Route.objects.filter(**filters).order_by('-'+terrain_type)[:50]

        return routes

class StyleTypes(models.Model):
    def get_routes(style, **filters):
        
        filters[style] = True
        filters['bayes__gte'] = 3.5

        routes = Route.objects.filter(**filters).order_by('-bayes')[:50]

        return routes

    def get_areas(style, **filters):

        filters[style+'__gte'] = 0.75

        areas = Area.objects.filter(**filters).order_by('-bayes')[:50]
        return areas






