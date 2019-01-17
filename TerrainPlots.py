# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 17:51:55 2019

@author: Bob
"""

import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import numpy as np


database = 'Routes-Cleaned.sqlite'
database = database.replace('\\', '/')
conn = sqlite3.connect(database)
query = 'SELECT name, slab, overhang, crack, chimney, arete FROM Routes LIMIT 1000'
routes = pd.read_sql(query, con=conn)
plt.scatter(routes['slab'], routes['chimney'])

routes = pd.read_sql(query, con=conn).sort_values(by='overhang').reset_index(drop=True)
plt.scatter(routes['slab'], routes['overhang'])

routes = pd.read_sql(query, con=conn).sort_values(by='crack').reset_index(drop=True)
plt.scatter(routes['slab'], routes['crack'])
