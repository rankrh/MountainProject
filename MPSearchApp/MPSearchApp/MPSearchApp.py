from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.rangeslider import RangeSlider
from kivy.core.window import Window
import sqlite3

path = 'C:\\Users\\Bob\\Documents\\Python\\Mountain Project\\'
conn = sqlite3.connect(path + 'Routes-Cleaned.sqlite')
cursor = conn.cursor()

class SearchLayout(BoxLayout):

    def __init__(self):
        super(SearchLayout, self).__init__()
       
    sport = False
    trad = False
    tr = False
    boulder = False
    mixed = False
    ice = False
    snow = False
    aid = False
    alpine = False
    
    def pitch_text(self, values):
        low = int(values[0])
        high = int(values[1])
        
        text = '%s to %s pitches' % (low, high)
        
        if high == 11:
            text = '%s or more pitches' % low
            
        return text

    def manage_ropes(self):
        if self.sport or self.tr or self.trad:
            self.ids.rope_slide.disable = False
            self.ids.rope_diff.opacity = 1.0
            self.ids.rope_slide.opacity = 1.0
        elif not self.sport and not self.tr and not self.trad:
            self.ids.rope_slide.disable = True
            self.ids.rope_diff.opacity = 0.0
            self.ids.rope_slide.opacity = 0.0

    def sport_diff(self):
        self.sport= not self.sport
        self.manage_ropes()


    def trad_diff(self):
        self.trad = not self.trad
        self.manage_ropes()
        
        
        
    def tr_diff(self):
        self.tr = not self.tr
        self.manage_ropes()    
        
        
    def conversion(self, d_range, style):
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

        conversion = {'rope': rope_conv, 'boulder': boulder_conv,
                       'mixed': mixed_conv, 'aid': aid_conv,
                       'ice': ice_conv, 'snow': snow_conv, 'alpine': alp_conv}

        low = int(d_range[0])
        high = int(d_range[1])
        
        grades = conversion[style]
        if high == 100:
            high = len(grades) - 1
        
        text = str(grades[low]) + ' to ' + str(grades[high])
        
        return  text


    def boulder_diff(self):
        self.boulder = not self.boulder
        if self.boulder:
            self.ids.boulder_slide.disable = False
            self.ids.boulder_diff.opacity = 1.0
            self.ids.boulder_slide.opacity = 1.0
        elif not self.boulder:
            self.ids.boulder_slide.disable = True
            self.ids.boulder_diff.opacity = 0.0
            self.ids.boulder_slide.opacity = 0.0


    def mixed_diff(self):
        self.mixed = not self.mixed
        if self.mixed:
            self.ids.mixed_slide.disable = False
            self.ids.mixed_diff.opacity = 1.0
            self.ids.mixed_slide.opacity = 1.0
        elif not self.mixed:
            self.ids.mixed_slide.disable = True
            self.ids.mixed_diff.opacity = 0.0
            self.ids.mixed_slide.opacity = 0.0
        
        
            
    def ice_diff(self):
        self.ice = not self.ice
        if self.ice:
            self.ids.ice_slide.disable = False
            self.ids.ice_diff.opacity = 1.0
            self.ids.ice_slide.opacity = 1.0
        elif not self.ice:
            self.ids.ice_slide.disable = True
            self.ids.ice_diff.opacity = 0.0
            self.ids.ice_slide.opacity = 0.0
        


    def snow_diff(self):
        self.snow = not self.snow
        if self.snow:
            self.ids.snow_slide.disable = False
            self.ids.snow_diff.opacity = 1.0
            self.ids.snow_slide.opacity = 1.0
        elif not self.snow:
            self.ids.snow_diff.disable = True
            self.ids.snow_diff.opacity = 0.0
            self.ids.snow_slide.opacity = 0.0
        
            

    def aid_diff(self):
        self.aid = not self.aid
        if self.aid:
            self.ids.aid_slide.disable = False
            self.ids.aid_diff.opacity = 1.0
            self.ids.aid_slide.opacity = 1.0
        elif not self.aid:
            self.ids.aid_slide.disable = True
            self.ids.aid_diff.opacity = 0.0
            self.ids.aid_slide.opacity = 0.0
        


    def alpine_diff(self):
        self.alpine = not self.alpine
        if self.alpine:
            self.ids.alpine_slide.disable = False
            self.ids.alpine_diff.opacity = 1.0
            self.ids.alpine_slide.opacity = 1.0
        elif not self.alpine:
            self.ids.alpine_slide.disable = True
            self.ids.alpine_diff.opacity = 0.0
            self.ids.alpine_slide.opacity = 0.0  


    def danger_conv(self, max_danger):
        danger = ['G', 'PG13', 'R', 'X']
        return danger[int(max_danger)] + ' and under'
        
        
    
class MPSearchApp(App):
    def build(self):
        return SearchLayout()


if __name__ == '__main__':

    MPSearchApp().run()