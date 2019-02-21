from django.urls import path

from . import views


app_name = 'routefinder'
urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('results/', views.results, name='results'),
    path('route/<int:route_id>', views.route, name='route'),
]