# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
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

    def find_terrain_types(self):
        terrain = {
            'arete': self.arete,
            'chimney': self.chimney,
            'crack': self.crack,
            'slab': self.slab,
            'overhang': self.overhang
        }


        terrain_types = []
        for terrain_type, terrain_score in terrain.items():
            if terrain_score >= 0.95:
                terrain_types.append(terrain_type)

        if len(terrain_types) == 0:
            return 'Unknown'
        return terrain_types

