from googlemaps.haversine import Haversine
from googlemaps.geocode import GeoCode
import pandas as pd
import numpy as np
import sqlite3
import re
import os
import random

import kivy

from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen
from kivy.uix.rangeslider import RangeSlider
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

from kivy.lang import Builder

from kivy.app import App

from kivy.properties import StringProperty

# Connects to DB
conn = sqlite3.connect('Routes-Cleaned.sqlite')

# Used to grab human-readable grading system
decode_systems = {
    'sport': 'yds_rating',
    'trad': 'yds_rating',
    'tr': 'yds_rating',
    'boulder': 'hueco_rating',
    'ice': 'ice_rating',
    'snow': 'snow_rating',
    'aid': 'aid_rating',
    'mixed': 'mixed_rating'}

# Counts routes in a given area group
def get_counts(area_group):
    if area_group.name != -1:
        area_group['area_counts'] = len(area_group)
    else:
        area_group['area_counts'] = 1        
    return area_group

# Grabs random picture from file to use as background
def global_background():
    path = 'C:/Users/Bob/Documents/Python/Mountain Project/images/backgrounds/'
    pics = os.listdir(path)
    pic = random.choice(pics)
    path += pic
    return path

class ScrollableLabel(ScrollView):
    text = StringProperty('')

# Only allows user to input digits and a single period
class FloatInput(TextInput):
    pat = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)


# First page
class StylesPage(Screen):

     
    def get_background(self):
        return global_background()

    styles = {
        'sport': {
            'search': False,
            'slider_id': 'sport_slide',
            'label_id': 'sport_diff',
            'grades': (None, None),
            'system': 'yds_rating'}, 
        'trad': {
            'search': False,
            'slider_id': 'trad_slide',
            'label_id': 'trad_diff',
            'grades': (None, None),
            'system': 'yds_rating'},
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
            'grades': (None, None),
            'system': 'hueco_rating'},
        'mixed': {
            'search': False,
            'slider_id': 'mixed_slide',
            'label_id': 'mixed_diff',
            'grades': (None, None),
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

    conversion = {
        'sport': rope_conv,
        'trad': rope_conv,
        'tr': rope_conv,
        'boulder': boulder_conv,
        'mixed': mixed_conv,
        'aid': aid_conv,
        'ice': ice_conv,
        'snow': snow_conv}

    def set_style(self, style):
        self.styles[style]['search'] = not self.styles[style]['search']
        slider = self.styles[style]['slider_id']
        label = self.styles[style]['label_id']

        if self.styles[style]['search']:
            self.ids[slider].disable = False
            self.ids[slider].opacity = 1.0
            self.ids[label].opacity = 1.0

            self.difficulty_conversion(style, self.ids[slider].value)

        elif not self.styles[style]['search']:
            self.ids[slider].disable = True
            self.ids[slider].opacity = 0.0
            self.ids[label].opacity = 0.0


    def difficulty_conversion(self, style, difficulty_range):
        low = int(difficulty_range[0])
        high = int(difficulty_range[1])
        self.styles[style]['grades'] = (low, high)
        
        grades = self.conversion[style]
        if high == 100:
            high = len(grades) - 1
        
        text = str(grades[low]) + ' to ' + str(grades[high])
        label = self.styles[style]['label_id']

        self.ids[label].text = text

    def get_styles(self):
        return self.styles

class PreferencesPage(Screen):
    preferences = {
        'pitches': (None, None), 
        'danger': 3, 
        'commitment': 3,
        'location': {
            'name': None,
            'coordinates': (None, None)},
        'distance': None,
        'features': {
            'arete': False,
            'chimney': False,
            'crack': False,
            'slab': False,
            'overhang': False}}

    def get_background(self):
        return global_background()
            
    def set_up(self, styles):
        pitches = False
        multipitch_styles = [
            'sport', 'trad', 'aid', 'mixed', 'alpine', 'snow', 'ice']
        
        for style in multipitch_styles:
            if style in styles.keys():
                if styles[style]['search']:
                    pitches = True
                    break

        if pitches:
            self.ids.pitches.opacity = 1
            self.ids.pitch_num.opacity = 1
            self.ids.pitch_num.disable = False
            self.ids.pitch_prompt.opacity = 1
        
        elif not pitches:
            self.ids.pitches.opacity = 0
            self.ids.pitch_num.opacity = 0
            self.ids.pitch_num.disable = True
            self.ids.pitch_prompt.opacity = 0


    def danger_conv(self, max_danger):
        danger = ['G', 'PG13', 'R', 'All Danger Levels']
        self.preferences['danger'] = max_danger
        if max_danger < 3:
            return danger[int(max_danger)] + ' and under'
        else:
            return danger[int(max_danger)]
        
    def commitment_conv(self, max_commitment):
        commitment =  ['I', 'II', 'III', 'IV', 'V', 'VI']
        self.preferences['commitment'] = max_commitment
        if max_commitment < 5:
            return commitment[int(max_commitment)] + ' and under'
        else:
            return commitment[int(max_commitment)]

    def pitch_text(self, values):
        low = int(values[0])
        high = int(values[1])
        self.preferences['pitches'] = (low, high)
        
        if low == high:
            if high == 11:
                return '%s or more pitches' % low
            else:
                return '%s pitches' % high
        elif high == 11:
            return '%s or more pitches' % low
        elif low == 0:
            return 'Up to %s pitches' % high
        else:
            text = '%s to %s pitches' % (low, high)


        return text

    def get_location(self, location): 
        if location is not '':  
            self.preferences['location']['name'] = location

    def get_distance(self, distance):
        if distance is not '':
                self.preferences['distance'] = int(distance)
    
    def set_feature(self, feature):
        features = self.preferences['features']
        features[feature] = not features[feature]

    def get_preferences(self):
        return self.preferences

class ResultsPage(Screen):
    def get_background(self):
        return global_background()

    def get_routes(self, styles, preferences, width):

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

        multipitch_styles = [
            'sport', 'trad', 'aid', 'mixed', 'alpine', 'snow', 'ice']

        pitch_range = preferences['pitches']

        query = 'SELECT * FROM Routes'
    
        search = []
        first = True
        ignore = []
        
        systems = []

        for style, data in styles.items():
            if data['search']:
                search.append(style)
                decoded = decode_systems[style]
                if decoded not in systems:
                    systems.append(decoded)
            else:
                ignore.append(style)
                
        for style in search:
            if first:
                joiner = ' WHERE'
            else:
                joiner = ' OR'
            first = False

            pitches = ''
            
            if style in multipitch_styles:  
                if pitch_range[1] < 11:
                    pitches = ' AND pitches BETWEEN %s AND %s' % pitch_range
                elif pitch_range[1] == 11:
                    pitches = ' AND pitches > %s' % pitch_range[0]
            keys = (joiner, style, pitches)
            query += '%s (%s is 1%s)' % (keys)
        
        if len(search) >= 1:
            for style in ignore:
                query += ' AND %s = 0' % style

        routes = pd.read_sql(query, con=conn, index_col='route_id')

        if len(routes) == 0:
            self.ids.test.text = query
            return

        danger = preferences['danger']
        routes = routes[routes['danger_conv'].values <= danger]
        if len(routes) == 0:
            self.ids.test.text = 'No routes available that safe.  Try expanding your danger levels'
            return


        location = preferences['location']
        location_name = location['name']
        coordinates = location['coordinates']

        if location_name is not None:
            location['coordinates'] = GeoCode(location_name)
            print(location_name)

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
            self.ids.test.text = 'No routes available that close to you.  Try expanding your distance search.'
            return
            
        routes = routes.groupby('area_group').apply(get_counts)

        routes['value'] = (
            (100 * routes['bayes'] * np.log(routes['area_counts'] + 0.001) + np.e)
            / (routes['distance'] ** 2))

        routes = routes.head(10).sort_values(by='value', ascending=False)
        routes.rename(columns={'name': 'Name'}, inplace=True)
        routes = routes.set_index('Name')
        routes['Rating'] = routes['bayes'].round(1)

        routes['Grade'] = routes[systems].apply(
            lambda x: ','.join(x.dropna().astype(str)), axis=1)

        terrain = ['arete', 'chimney', 'crack', 'slab', 'overhang']
        routes['Style'] = routes[terrain].idxmax(axis=1)
        routes['val'] = routes[terrain].max(axis=1)
        routes.loc[routes['val'] < 0.75, 'Style'] = ''

        display_columns = ['Rating', 'Grade', 'Style']
        routes = routes[display_columns]
        routes = routes.to_dict('index')

        self.ids.routes.cols = 4
        self.ids.routes.add_widget(Label(text='Name'))

        for column in display_columns:
            self.ids.routes.add_widget(Label(text=column))

        for route, data in routes.items():
            self.ids.routes.add_widget(Label(text=route))
            for value in data.values():
                self.ids.routes.add_widget(Label(text=str(value)))

class RoutesScreenManager(ScreenManager):
    pass

root_widget = Builder.load_file('RouteFinder.kv')

class RouteFinder(App):
    def build(self):
        return root_widget

if __name__ == '__main__':
    RouteFinder().run() 



