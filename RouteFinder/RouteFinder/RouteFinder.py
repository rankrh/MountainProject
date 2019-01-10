from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

class SearchPage(BoxLayout):
    pass

class RouteFinder(App):
    def build(self):
        return SearchPage()

if __name__ == '__main__':
    RouteFinder().run() 



