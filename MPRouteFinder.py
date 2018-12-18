# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 10:58:04 2018

@author: Bob
"""

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from mymods import geocode
import numpy as np
import pandas as pd
import sqlite3
import ssl

API_KEY = 'AIzaSyDIKSmBNfW1uGhp5MdD9YsY8WncGkdNsio'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('Routes-Cleaned.sqlite')
cursor = conn.cursor()

pd.options.display.max_rows = 100
pd.options.display.max_columns = 37



###############################################################################
########################   GETTING ROUTE TYPE   ###############################
###############################################################################



route_types = {'trad': False, 'tr': False, 'sport': True, 'aid': False,
                  'snow': False, 'ice': False, 'mixed': False,
                  'boulder': False, 'alpine': False}

text = 'SELECT * FROM Routes\nWHERE '
for route in route_types:
    if route_types[route]:
        text += route + ' = 1\nOR '
text = text[:-3]
text += 'AND '
for route in route_types:
    if not route_types[route] and route is not 'tr':
        text += route + ' = 0\nAND '
text = text[:-4]
routes = pd.read_sql(text, con=conn)
routes  = routes.dropna(subset=['latitude'])

avg_stars = np.mean(routes['stars'])


###############################################################################
########################   GETTING ROUTE DIFF   ###############################
###############################################################################



diff_conv = {
    'rope_conv': ['3rd', '4th', 'Easy 5th', '5.0', '5.1', '5.2', '5.3', '5.4',
             '5.5', '5.6', '5.7', '5.7+', '5.8-', '5.8', '5.8+', '5.9-',
             '5.9', '5.9+', '5.10a', '5.10-', '5.10a/b', '5.10b', '5.10',
             '5.10b/c', '5.10c', '5.10+', '5.10c/d', '5.10d', '5.11a',
             '5.11-', '5.11a/b', '5.11b', '5.11', '5.11b/c', '5.11c',
             '5.11+', '5.11c/d', '5.11d', '5.12a', '5.12-', '5.12a/b',
             '5.12b', '5.12', '5.12b/c', '5.12c', '5.12+', '5.12c/d',
             '5.12d', '5.13a', '5.13-', '5.13a/b', '5.13b', '5.13',
             '5.13b/c', '5.13c', '5.13+', '5.13c/d', '5.13d', '5.14a',
             '5.14-', '5.14a/b', '5.14b', '5.14', '5.14b/c', '5.14c',
             '5.14+', '5.14c/d', '5.14d', '5.15a', '5.15-', '5.15a/b',
             '5.15b', '5.15', '5.15c', '5.15+', '5.15c/d', '5.15d'],
    'boulder_conv': ['V-easy', 'V0-', 'V0', 'V0+', 'V0-1', 'V1-', 'V1', 'V1+',
                 'V1-2', 'V2-', 'V2', 'V2+', 'V2-3', 'V3-', 'V3', 'V3+',
                 'V3-4', 'V4-', 'V4', 'V4+', 'V4-5', 'V5-', 'V5', 'V5+',
                 'V5-6', 'V6-', 'V6', 'V6+', 'V6-7', 'V7-', 'V7', 'V7+',
                 'V7-8', 'V8-', 'V8', 'V8+', 'V8-9', 'V9-', 'V9', 'V9+',
                 'V9-10', 'V10-', 'V10', 'V10+', 'V10-11', 'V11-', 'V11',
                 'V11+', 'V11-12', 'V12-', 'V12', 'V12+', 'V12-13', 'V13-',
                 'V13', 'V13+', 'V13-14', 'V14-', 'V14', 'V14+', 'V14-15',
                 'V15-', 'V15', 'V15+', 'V15-16', 'V16-', 'V16', 'V16+',
                 'V16-17', 'V17-', 'V17'],
    'mixed_conv': ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10',
              'M11', 'M12'],

    'aid_conv': ['A0', 'A1', 'A2', 'A2+', 'A3', 'A3+', 'A4', 'A4+', 'A5', 'A6'],
    'ice_conv': ['WI1', 'WI2', 'WI3', 'WI4', 'WI5', 'WI6', 'WI7', 'WI8'],
    'danger_conv': ['PG13', 'R', 'X'],
    'snow_conv': ['Easy', 'Mod', 'Steep']}
 


low_end = '5.8'
high_end = '5.12'

low_val = diff_conv['rope_conv'].index(low_end)
high_val = diff_conv['rope_conv'].index(high_end)
routes = routes[(routes['rope_conv'] >= low_val) & 
                (routes['rope_conv'] <= high_val)]
###############################################################################
########################   GETTING ROUTE DIST   ###############################
###############################################################################

loc = geocode.get_lat_long('Estes Park')
routes['distance'] = geocode.haversine(loc[0], loc[1],
      routes['latitude'], routes['longitude'])
    
###############################################################################
########################   GETTING ROUTE QUAL   ###############################
###############################################################################
# Move to cleaner

routes['bayes'] = (((routes['votes'] * routes['stars']) + (10 * avg_stars))
                    / (routes['votes'] + 10))

#Bayesian est. = (1350x10 + 1300x6.7) / (1350+1300) = 8.4

###############################################################################
########################   GETTING ROUTE AREAS    #############################
###############################################################################
# Move to cleaner

lats = routes['latitude'].tolist()
longs= routes['longitude'].tolist()
locs = []

for x in range(len(lats)):
    locs.append((lats[x], longs[x]))

locs = StandardScaler().fit_transform(locs)
db = DBSCAN(eps=0.007, min_samples=3).fit(locs)
core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_
unique, counts = np.unique(labels, return_counts=True)
counts = dict(zip(unique, counts))
area_counts = []
for label in labels:
    if label >=0:
        area_counts.append(counts[label])
    elif label == -1:
        area_counts.append(1)
        
routes['area_group'] = labels
routes['area_counts'] = area_counts

# Plot result
import matplotlib.pyplot as plt

# Black removed and is used for noise instead.
unique_labels = set(labels)
colors = [plt.cm.Spectral(each)
          for each in np.linspace(0, 1, len(unique_labels))]
for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = [0, 0, 0, 1]

    class_member_mask = (labels == k)

    xy = locs[class_member_mask & core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
             markeredgecolor='k', markersize=14)

    xy = locs[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
             markeredgecolor='k', markersize=6)

plt.show()

###############################################################################
########################   COMBINE ALL METRICS    #############################
###############################################################################

routes['value'] = ((100 * routes['bayes'] * np.log(routes['area_counts'])) /
                  (routes['distance'] ** 2))

for url in routes.sort_values(by='value', ascending=False)['url'].head():
    print(url)
    
print()
for d in routes.sort_values(by='value', ascending=False)['distance'].head():
    print(d)

print()
for d in routes.sort_values(by='distance', ascending=True)['url'].head():
    print(d)
