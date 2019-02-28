from django.urls import path

from . import views


app_name = 'routefinder'
urlpatterns = [
    path('', views.search, name='search'),
    path('results/', views.results, name='results'),
    path('route/<int:route_id>', views.route, name='route'),
    path('area/<int:area_id>', views.area, name='area'),
    path('browse/', views.browse, name='browse'),
]