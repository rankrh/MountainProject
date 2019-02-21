from django.db import models

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
    error = models.TextField(blank=True, null=True)
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

    def terrain_types(self):
        terrain = {
            'arete': self.arete,
            'chimney': self.chimney,
            'crack': self.crack,
            'slab': self.slab,
            'overhang': self.overhang
        }

        terrain_types = ''
        return terrain
        for terrain_type, terrain_score in terrain.items():
            if terrain_score >= 0.75:
                terrain_types += f' {terrain_type}({terrain_score})'

        if len(terrain_types) == 0:
            terrain_type = list(terrain.keys())
            terrain_score = list(terrain.values())
            most_likely_terrain = terrain_type[terrain_score.index(max(terrain_score))]
            return f'{most_likely_terrain}({max(terrain_score)})'
        
        return terrain_types

    def other_routes_in_area(self):
        other_routes = Route.objects.filter(area_id=self.area_id)
        other_routes = other_routes.exclude(name=self.name)
        other_routes = other_routes.order_by('-bayes')

        return other_routes

    def similar_routes_nearby(self):
        
        route_information = {
            'sport': {
                'search': self.sport,
                'grade': self.rope_conv,
                'system': 'rope_conv'},
            'trad': {
                'search': self.trad,
                'grade': self.rope_conv,
                'system': 'rope_conv'},
            'tr': {
                'search': self.tr,
                'grade': self.rope_conv,
                'system': 'rope_conv'},
            'boulder': {
                'search': self.boulder,
                'grade': self.boulder_conv,
                'system': 'boulder_conv'},
            'mixed': {
                'search': self.mixed,
                'grade': self.mixed_conv,
                'system': 'mixed_conv'},
            'snow': {
                'search': self.snow,
                'grade': self.snow_conv,
                'system': 'snow_conv'},
            'aid': {
                'search': self.aid,
                'grade': self.aid_conv,
                'system': 'aid_conv'},
            'ice': {
                'search': self.ice,
                'grade': self.ice_conv,
                'system': 'ice_conv'},
            'alpine': {
                'search': self.alpine,
                'grade': self.nccs_conv,
                'system': 'nccs_conv'}}

        filters = {'area_group': self.area_group}

        for style, data in route_information.items():
            filters[style] = data['search']
            if data['search']:
                system_name = data['system']
                filters[style] = data['search']
                filters[system_name] = data['grade']

        other_routes = Route.objects.filter(**filters)
        other_routes = other_routes.exclude(name=self.name)
        other_routes = other_routes.order_by('-bayes')

        return other_routes
