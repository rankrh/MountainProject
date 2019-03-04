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
    name = models.TextField(blank=True, null=True)
    url = models.TextField(unique=True, blank=True, null=True)
    from_id = models.IntegerField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    child_routes = None
    main_style = None
    
    class Meta:
        managed = False
        db_table = 'areas'

    def get_areas(self):
        path = [self.id]
        if self.from_id is not None:
            parent = Area.objects.get(pk=self.from_id)
            parent = parent.get_areas()
            for area in parent:
                path.append(area)
        return path

    def parent_areas(self):
        path = self.get_areas()

        path = [Area.objects.get(pk=area) for area in path]
        return path

    def children_areas(self):

        children = Area.objects.filter(from_id=self.id)

        if len(children) == 0:
            children = Route.objects.filter(area_id=self.id)
            if len(children) > 0:
                self.child_routes = children
        
        return children

    def terrain(self):
        if self.child_routes is not None:
            number_of_children = len(self.child_routes)
            terrain = pd.Series(
                [0] * len(terrain_types),
                index = terrain_types)
            terrain['Unknown'] = 0

            for child in self.child_routes:
                child_terrain = child.get_terrain_types()
                if child_terrain is not None:
                    for t_type, score in child_terrain.items():
                        terrain_type_known = False
                        if score > 50:
                            terrain[t_type] += 1
                            terrain_type_known = True
                        if not terrain_type_known:
                            terrain['Unknown'] += 1

                else:
                    terrain['Unknown'] += 1

            terrain = 100 * terrain / sum(terrain)
            terrain = terrain.round(0)

            return terrain.to_dict()

    def styles(self):
        if self.child_routes is not None:
            child_styles = pd.Series(
                [0] * (len(climbing_styles) + 1),
                index = climbing_styles + ['alpine'])

            for child in self.child_routes:
                child_style = {
                    'sport': child.sport,
                    'trad': child.trad,
                    'tr': child.tr,
                    'boulder': child.boulder,
                    'mixed': child.mixed,
                    'aid': child.aid,
                    'ice': child.ice,
                    'snow': child.snow,
                    'alpine': child.alpine
                    }
                for style, value in child_style.items():
                    if value:
                        child_styles[style] += 1
            self.main_style = child_styles.idxmax()
            return self.main_style

    def grades(self):
        if self.child_routes is not None and self.main_style is not None:
            number_of_children = len(self.child_routes)
            if number_of_children > 0:
                score = 0
                
                for child in self.child_routes:
                    score += getattr(child, climb_style_to_system[self.main_style])

                score = score // number_of_children

                score = climb_style_to_grade[self.main_style][int(score)]

                return score


class Route(models.Model):
    arete = models.FloatField(blank=True, null=True)
    chimney = models.FloatField(blank=True, null=True)
    crack = models.FloatField(blank=True, null=True)
    slab = models.FloatField(blank=True, null=True)
    overhang = models.FloatField(blank=True, null=True)
    word_count = models.FloatField(blank=True, null=True)
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
    error = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Routes_scored'

    def __str__(self):
        return self.name

    def format_terrain(self):
        terrain = {
            'arete': round(self.arete, 2),
            'chimney': round(self.chimney, 2),
            'slab': round(self.slab, 2),
            'overhang': round(self.overhang, 2),
            'crack': round(self.crack, 2)
            }

        for style, value in terrain.items():
            if value >= 0.95:
                terrain[style] = "Definitely"
            elif value >= 0.75:
                terrain[style] = "Almost certainly"
            elif value >= 0.5:
                terrain[style] = "Probably"
            elif value >= 0.15:
                terrain[style] = "Probably no"
            else:
                terrain[style] = "Almost certainly no"

        return terrain

    def get_terrain_types(self):

        terrain = pd.Series([
            int(round(self.arete, 1) * 100),
            int(round(self.chimney, 1) * 100),
            int(round(self.slab, 1) * 100),
            int(round(self.overhang, 1) * 100),
            int(round(self.crack, 1) * 100)],
            index=terrain_types)

        if len(terrain[terrain >= 30]) == 0:
            return
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
            filters["pitches__gte"] = self.pitches - 2

        other_routes = Route.objects.filter(**filters)
        other_routes = other_routes.exclude(name=self.name)
        if len(other_routes) == 0:
            return

        other_routes = other_routes.order_by('-bayes')


        return other_routes

    def area(self):
        parents = get_object_or_404(Area, id=self.area_id)
        parents = parents.parent_areas()

        parents = parents[::-1]

        return parents

    def route_style(self):

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
        
        route_styles = list(route_styles[route_styles == True].index)

        return route_styles

    def grade_conversion(self):
        return {}

    def route_grade(self):
        grades = {
            'YDS': self.yds_rating,
            'French': self.french_rating,
            'Ewbank': self.ewbanks_rating,
            'UIAA': self.uiaa_rating,
            'South Africa': self.za_rating,
            'British': self.british_rating,
            'Hueco': self.hueco_rating,
            'Fontaine Bleu': self.font_rating,
            'Mixed': self.mixed_rating,
            'Aid': self.aid_rating,
            'Snow': self.snow_rating,
            'Ice': self.ice_rating}

        grades = {system: grade for system, grade in grades.items() if grade is not None}

        return grades

    def best_routes(get_request):
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

        query = 'SELECT * FROM "Routes_scored"'
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
            lambda x: ', '.join(x.dropna()), axis=1
        )
        # Selects the top ten routes
        routes = routes.sort_values(by='value', ascending=False)

        display_columns = [
            'id', 'name', 'bayes', 'terrain', 'style', 'pitches',
            'length', 'url', 'area_group', 'area_counts', 'rope_grades',
            'boulder_grades', 'mixed_rating', 'aid_rating', 'snow_rating',
            'ice_rating', 'distance']

        routes['area_counts'] = routes['area_counts'] - 1
        routes = routes[display_columns]

        routes = routes.to_dict(orient='records')

        return routes