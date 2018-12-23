# -*- coding: utf-8 -*-
"""
Created on Sat Dec 22 13:46:09 2018

@author: Bob
"""

import pandas as pd
import sqlite3

conn = sqlite3.connect('Routes-Cleaned.sqlite')
cursor = conn.cursor()

path = 'Descriptions/TFIDF.csv'
pd.options.display.max_rows = 200000

def conversion_to_side_by_side():
    archetypes = pd.read_csv(filepath_or_buffer=path,
                             index_col=['style','word'])['tfidfn']
    arete = archetypes.loc['arete'].rename('arete')
    chimney = archetypes.loc['chimney'].rename('chimney')
    crack = archetypes.loc['crack'].rename('crack')
    slab = archetypes.loc['slab'].rename('slab')
    overhang = archetypes.loc['overhang'].rename('overhang')
    
    archetypes = pd.concat([arete, chimney, crack, slab, overhang],
                           axis=1,
                           sort=True)
    
    archetypes.to_csv(path)
    
def cossim(route, archetypes):
    print(archetypes['arete'])    

cursor.execute('''CREATE TABLE IF NOT EXISTS Terrain(
                    route_id INTEGER,
                    arete FLOAT,
                    chimney FLOAT,
                    crack FLOAT,
                    slab FLOAT,
                    overhang FLOAT)''')

archetypes = pd.read_csv(filepath_or_buffer=path,
                         index_col='word')
query = '''SELECT route_id, word, tfidfn
           FROM TFIDF
           WHERE route_id < 10'''
           #NOT IN (SELECT route_id FROM Terrain)'''
           
routes = pd.read_sql(query, con=conn, index_col='route_id') #.groupby(level=0)
#routes = routes.apply(cossim, archetypes)
cossim(1, archetypes)

















