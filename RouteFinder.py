# -*- coding: utf-8 -*-
"""
Created on Thu Jam 10 3:42 2019

@author: Bob

Summary:
Allows users to search for data and displays it in a useful way.

Details:  
After gathering, cleaning, and analyzing data, this program is run to create
the UI.  It firsts prompts the user for preferences on a variety of metrics,
including type of route, difficulty, location, maximum distance, danger levels,
and number of pitches.  It then sifts through the database to find routes that
fit these parameters, then organizes them based on their quality, distance,
and the number of other similar routes nearby.    
"""

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

def background(path):
    """Returns image to use as background.
    
    Images are public domain, found at: https://www.pexels.com/
    
    Args:
        path(str): Location of folder to choose picture from
    Returns:
        path(str): Location of randomly chosen picture in a given file"""
    pics = os.listdir(path)
    pic = random.choice(pics)
    path += pic
    return path

class FloatInput(TextInput):
    """A form of text input that limits characters to digits and a single
    period. Used to prevent users from entering data that should only be
    numeric.

    Attributes:
        pat:Allowable characters

    Methods:
        insert_text     Allows user to input numeric data
    """

    pat = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        """Allows users to input numeric data as any number of digits and 1
        period
        
        Overwrites the default Kivy behavior, which allows all characters.

        Args:
            substring(str): String to display in the text box
            from_undo(Bool): Defaults to False.  True if use presses ctrl+z
        """
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)


class StylesPage(Screen):
    """Screen that shows users the available styles and grades.

    Attributes:
        styles (dict): Holds information on the user's style choices, and how
            to reference different parts of the kv file.  Contains a dictionary
            for each style:
                'search' - (Boolean defaults to False) Whether user has
                    selected that style
                'slider_id' - (string) kv ID for the difficulty slider
                'label_id' - (string) kv ID for the difficulty label
                'Grades' - (tuple, defaults to None, None) Upper and lower
                    bounds for the user difficulty range.
                'system' - (string) Name of the database column that holds the
                    human-readable grading system.  Applies to climbing styles
                    with multiple systems.  At this point, each style only
                    supports one system.
        rope_conv (list): Ordered list of route difficulties in human readable
            format. Used for sport, trad, and tr routes.  Only Yosemite Decimal
            System (YDS) is supported right now.
        boulder_conv (list): Ordered list of route difficulties in human
            readable format. Used for bouldering routes.  Only Hueco rating
            system is supported
        mixed_conv (list): Ordered list of route difficulties in human readable
            format.  Used for mixed routes.
        aid_conv (list): Ordered list of route difficulties in human readable
            format. Used for Aid routes
        snow_conv (list): Ordered list of route difficulties in human readable
            format. Used for snow routes.
        ice_conv(list): Ordered list of route difficulties in human readable
            format. Used for ice routes.
        conversion (dict): Links the type of route with the conversion list.
        photo (str): Runs background function to get background picture and
            returns path

    Methods:
        set_style: Updates style attribute to reflect the user's style choices
            and difficulty levels and updates widgets in kv file.
        get_style: Returns style attribute.
        difficulty_conversion: Updates styles to reflect user choices for
            difficulty range, then converts number to corresponding difficulty
            in human readable format and updates kv. 

    """
     
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
    ice_conv = []

    conversion = {
        'sport': rope_conv,
        'trad': rope_conv,
        'tr': rope_conv,
        'boulder': boulder_conv,
        'mixed': mixed_conv,
        'aid': aid_conv,
        'ice': ice_conv,
        'snow': snow_conv}

    photo = background(
        'C:/Users/Bob/Documents/Python/Mountain Project/images/backgrounds/')

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

    def get_styles(self):
        return self.styles

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


class PreferencesPage(Screen):
    preferences = {
        'pitches': (None, None), 
        'danger': 3, 
        'commitment': 3,
        'location': {
            'name': None,
            'coordinates': (None, None)},
        'distance': 500,
        'features': {
            'arete': False,
            'chimney': False,
            'crack': False,
            'slab': False,
            'overhang': False}}

    photo = background(
            'C:/Users/Bob/Documents/Python/Mountain Project/images/backgrounds/')
            
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
    photo = background(
            'C:/Users/Bob/Documents/Python/Mountain Project/images/backgrounds/')

    def get_routes(self, styles, preferences):

        print(styles, preferences)

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
        
        multipitch_styles = [
            'sport', 'trad', 'aid', 'mixed', 'alpine', 'snow', 'ice']

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
            pitch_range = preferences['pitches']
            if style in multipitch_styles:  
                if pitch_range[1] < 11:
                    pitches = ' AND pitches BETWEEN %s AND %s' % pitch_range
                elif pitch_range[1] == 11:
                    pitches = ' AND pitches > %s' % pitch_range[0]
            keys = (joiner, style, grades, pitches)
            query += '%s (%s is 1 AND %s%s)' % (keys)
        
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

        if location_name is not None:
            location['coordinates'] = GeoCode(location_name)
            print(location_name)

        coordinates = location['coordinates']   
        if all(coordinates):
            routes['distance'] = Haversine(
                coordinates,
                (routes['latitude'], routes['longitude']))
        else:
            routes['distance'] = 1

        distance = preferences['distance']
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
            lambda x: ', '.join(x.dropna().astype(str)), axis=1)

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



