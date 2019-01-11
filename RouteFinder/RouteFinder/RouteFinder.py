from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.rangeslider import RangeSlider


class SearchPage(BoxLayout):

    styles = {'sport': {'search': False, 'id': 'sport_slide'},
              'trad': {'search':False, 'id': 'trad_slide'},
              'tr': {'search': False, 'id': 'tr_slide'},
              'boulder': {'search': False, 'id': 'boulder_slide'},
              'mixed': {'search': False, 'id': 'mixed_slide'},
              'snow': {'search': False, 'id': 'snow_slide'},
              'aid': {'search': False, 'id': 'aid_slide'},
              'ice': {'search': False, 'id': 'ice_slide'},
              'alpine': {'search': False, 'id': 'alpine_slide'}}

    def __init__(self):
        super(SearchPage, self).__init__()

    def set_style(self, style):
        self.styles[style]['search'] = not self.styles[style]['search']
        style_id = self.styles[style]['id']
        
        if self.styles[style]['search']:
            self.ids[style_id].disable = False
            self.ids[style_id].opacity = 1.0
        elif not self.styles[style]['search']:
            self.ids[style_id].disable = True
            self.ids[style_id].opacity = 0.0


class RouteFinder(App):
    def build(self):
        return SearchPage()

if __name__ == '__main__':
    RouteFinder().run() 



