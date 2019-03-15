from django.urls import path

from . import views


app_name = 'routefinder'
urlpatterns = [
    path('', views.search, name='search'),
    path('results/', views.results, name='results'),
    path('route/<int:route_id>', views.route, name='route'),
    path('area/<int:area_id>', views.area, name='area'),
    path('browse/', views.browse, name='browse'),
    path('browse/terrain/', views.terrain, name='terrain'),
    path('browse/terrain/<str:terrain_type>', views.terrain_style, name="terrain_style"),
    path('browse/style', views.style, name='style'),
    path('browse/location', views.location, name='location'),
]