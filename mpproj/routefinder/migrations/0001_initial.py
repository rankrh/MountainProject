# Generated by Django 2.1.5 on 2019-02-19 22:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route_id', models.BigIntegerField(blank=True, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('url', models.TextField(blank=True, null=True)),
                ('bayes', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('trad', models.BooleanField(blank=True, null=True)),
                ('tr', models.BooleanField(blank=True, null=True)),
                ('sport', models.BooleanField(blank=True, null=True)),
                ('aid', models.BooleanField(blank=True, null=True)),
                ('snow', models.BooleanField(blank=True, null=True)),
                ('ice', models.BooleanField(blank=True, null=True)),
                ('mixed', models.BooleanField(blank=True, null=True)),
                ('boulder', models.BooleanField(blank=True, null=True)),
                ('alpine', models.BooleanField(blank=True, null=True)),
                ('pitches', models.FloatField(blank=True, null=True)),
                ('length', models.FloatField(blank=True, null=True)),
                ('nccs_conv', models.FloatField(blank=True, null=True)),
                ('boulder_conv', models.FloatField(blank=True, null=True)),
                ('rope_conv', models.FloatField(blank=True, null=True)),
                ('ice_conv', models.FloatField(blank=True, null=True)),
                ('snow_conv', models.FloatField(blank=True, null=True)),
                ('aid_conv', models.FloatField(blank=True, null=True)),
                ('mixed_conv', models.FloatField(blank=True, null=True)),
                ('danger_conv', models.FloatField(blank=True, null=True)),
                ('area_id', models.FloatField(blank=True, null=True)),
                ('area_group', models.FloatField(blank=True, null=True)),
                ('error', models.TextField(blank=True, null=True)),
                ('arete', models.FloatField(blank=True, null=True)),
                ('chimney', models.FloatField(blank=True, null=True)),
                ('crack', models.FloatField(blank=True, null=True)),
                ('slab', models.FloatField(blank=True, null=True)),
                ('overhang', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Routes_scored',
                'managed': False,
            },
        ),
    ]
