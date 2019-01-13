from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.rangeslider import RangeSlider
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
import os
import numpy as np

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

class StylesPage(Screen):

    styles = {'sport': {'search': False,
                        'slider_id': 'sport_slide',
                        'label_id': 'sport_diff'},
              'trad': {'search': False,
                       'slider_id': 'trad_slide',
                       'label_id': 'trad_diff'},
              'tr': {'search': False,
                     'slider_id': 'tr_slide',
                     'label_id': 'tr_diff'},
              'boulder': {'search': False,
                          'slider_id': 'boulder_slide',
                          'label_id': 'boulder_diff'},
              'mixed': {'search': False,
                        'slider_id': 'mixed_slide',
                        'label_id': 'mixed_diff'},
              'snow': {'search': False,
                       'slider_id': 'snow_slide',
                       'label_id': 'snow_diff'},
              'aid': {'search': False,
                      'slider_id': 'aid_slide',
                      'label_id': 'aid_diff'},
              'ice': {'search': False,
                      'slider_id': 'ice_slide',
                      'label_id': 'ice_diff'},
              'alpine': {'search': False,
                         'slider_id': 'alpine_slide',
                         'label_id': 'alpine_diff'}}

    rope_conv = ['3rd', '4th', 'Easy 5th', '5.0', '5.1', '5.2', '5.3',
                    '5.4', '5.5', '5.6', '5.7', '5.7+', '5.8-', '5.8', '5.8+',
                    '5.9-', '5.9', '5.9+', '5.10a', '5.10-', '5.10a/b',
                    '5.10b', '5.10', '5.10b/c', '5.10c', '5.10+', '5.10c/d',
                    '5.10d', '5.11a', '5.11-', '5.11a/b', '5.11b', '5.11',
                    '5.11b/c', '5.11c', '5.11+', '5.11c/d', '5.11d', '5.12a',
                    '5.12-', '5.12a/b', '5.12b', '5.12', '5.12b/c', '5.12c',
                    '5.12+', '5.12c/d', '5.12d', '5.13a', '5.13-', '5.13a/b',
                    '5.13b', '5.13', '5.13b/c', '5.13c', '5.13+', '5.13c/d',
                    '5.13d', '5.14a', '5.14-', '5.14a/b', '5.14b', '5.14',
                    '5.14b/c', '5.14c', '5.14+', '5.14c/d', '5.14d', '5.15a',
                    '5.15-', '5.15a/b', '5.15b', '5.15', '5.15c', '5.15+',
                    '5.15c/d', '5.15d']
    boulder_conv  = ['V-easy', 'V0-', 'V0', 'V0+', 'V0-1', 'V1-', 'V1',
                        'V1+', 'V1-2', 'V2-', 'V2', 'V2+', 'V2-3', 'V3-',
                        'V3', 'V3+', 'V3-4', 'V4-', 'V4', 'V4+', 'V4-5',
                        'V5-', 'V5', 'V5+', 'V5-6', 'V6-', 'V6', 'V6+',
                        'V6-7', 'V7-', 'V7', 'V7+', 'V7-8', 'V8-', 'V8',
                        'V8+', 'V8-9', 'V9-', 'V9', 'V9+', 'V9-10', 'V10-',
                        'V10', 'V10+', 'V10-11', 'V11-', 'V11', 'V11+',
                        'V11-12', 'V12-', 'V12', 'V12+', 'V12-13', 'V13-', 
                        'V13', 'V13+', 'V13-14', 'V14-', 'V14', 'V14+',
                        'V14-15', 'V15-', 'V15', 'V15+', 'V15-16', 'V16-',
                        'V16', 'V16+', 'V16-17', 'V17-', 'V17']
    mixed_conv = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9',
                    'M10', 'M11', 'M12']
    aid_conv = ['A0', 'A1', 'A2', 'A2+', 'A3',
                'A3+', 'A4', 'A4+', 'A5','A6']
    ice_conv = ['WI1', 'WI2', 'WI3', 'WI4', 'WI5', 'WI6', 'WI7', 'WI8']
    snow_conv = ['Easy', 'Mod', 'Steep']
    alp_conv =  ['I', 'II', 'III', 'IV', 'V', 'VI']

    conversion = {'sport': rope_conv, 'trad': rope_conv, 'tr': rope_conv,
                    'boulder': boulder_conv, 'mixed': mixed_conv,
                    'aid': aid_conv, 'ice': ice_conv, 'snow': snow_conv,
                    'alpine': alp_conv}

    def set_style(self, style):
        self.styles[style]['search'] = not self.styles[style]['search']
        slider = self.styles[style]['slider_id']
        label = self.styles[style]['label_id']

        if self.styles[style]['search']:
            self.ids[slider].disable = False
            self.ids[slider].opacity = 1.0
            self.ids[label].opacity = 1.0
        elif not self.styles[style]['search']:
            self.ids[slider].disable = True
            self.ids[slider].opacity = 0.0
            self.ids[label].opacity = 0.0

    def difficulty_conversion(self, style, difficulty_range):
        low = int(difficulty_range[0])
        high = int(difficulty_range[1])
        
        grades = self.conversion[style]
        if high == 100:
            high = len(grades) - 1
        
        text = str(grades[low]) + ' to ' + str(grades[high])
        label = self.styles[style]['label_id']

        self.ids[label].text = text

    def get_styles(self):
        return self.styles

class PreferencesPage(Screen):
    pitches = False
    preferences = {'pitches': (),
                   'danger': 3
                   }
    def set_up(self, styles):
        multipitch_styles = ['sport', 'trad', 'aid', 'mixed',
                             'alpine', 'snow', 'ice']
        for style in multipitch_styles:
            if style in styles.keys():
                if styles[style]['search']:
                    self.pitches = True
                    break

        if self.preferences['pitches']:
            self.ids.pitches.opacity = 1
            self.ids.pitches.size = (0, 0)
            self.ids.pitch_num.opacity = 1
            self.ids.pitch_num.disable = False

    def danger_conv(self, max_danger):
        danger = ['G', 'PG13', 'R', 'All Danger Levels']
        self.preferences['danger'] = max_danger
        if max_danger < 3:
            return danger[int(max_danger)] + ' and under'
        else:
            return danger[int(max_danger)]

    def pitch_text(self, values):
        low = int(values[0])
        high = int(values[1])
        self.preferences['pitches'] = (low, high)
        
        text = '%s to %s pitches' % (low, high)
        
        if high == 11:
            text = '%s or more pitches' % low
            
        return text

    def get_preferences(self):
        return self.preferences

class ResultsPage(Screen):
    def get_routes(self, styles, preferences,
                   location, key=GOOGLE_API_KEY):
        preferences['location'] = 
        styles['preferences'] = preferences
        self.ids.test.text = str(styles)
    

class RoutesScreenManager(ScreenManager):
    pass

root_widget = Builder.load_file('RouteFinder.kv')

class RouteFinder(App):
    def build(self):
        return root_widget

if __name__ == '__main__':
    RouteFinder().run() 



