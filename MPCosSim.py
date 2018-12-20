# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 10:41:49 2018

@author: Bob
"""

import pandas as pd
import sqlite3
import numpy as np


pd.options.display.max_rows = 200000
pd.options.display.max_columns = 1000

conn = sqlite3.connect('Routes-Cleaned.sqlite')
cursor = conn.cursor()

path = 'Descriptions/'

def tfidf_values():
    archetypes = pd.DataFrame()
    names = ['arete', 'chimney', 'crack', 'slab', 'overhang', 'face']
    
    for name in names:    
         tf = pd.read_csv(filepath_or_buffer=path + name)
         tf = tf.rename(columns={tf.columns[0]: 'word'})
         tf['style'] = name
         tf = tf.set_index(['style', 'word'])
         archetypes = pd.concat([archetypes, tf])     
     
    
    unique = archetypes.index.levels[1].unique().tolist()
    unique = tuple(unique)
    query = 'SELECT DISTINCT(word), idf from TFIDF WHERE word IN {}'.format(unique)
    idf = pd.read_sql(query, con=conn, index_col='word')
    
    def find_idf(word):
    
        try:
            val = idf.loc[word.name]['idf']
            word['idf'] = val
            word['tfidf'] = word['tf'] * word['idf']
            return word
            
        except KeyError:
            print(word.name, end=' ')
            print('Not in idf DF')
    archetypes = archetypes.groupby(level=[1]).apply(find_idf)
    archetypes = archetypes.reset_index(level=0, drop=True)
    
    print(archetypes)    
    archetypes.to_csv(path + 'TFIDF')

def normalize(routes):
    
    length = np.sqrt(np.sum(routes['tfidf'] ** 2))
    routes['tfidfn'] = routes['tfidf'] / length
    return routes


def get_tfidfn():
    styles = pd.read_csv(filepath_or_buffer=path+'TFIDF',
                         index_col=['style', 'word'])
    styles = styles.groupby('style').apply(normalize).sort_index(level=[0, 1])
    styles.to_csv(path + 'TFIDF')
    
def cos_sim(a, b):
    print(a.name)
    dot_prod =  np.sum(a['tfidfn'] * b)
    return dot_prod
 
normalized = pd.read_csv(filepath_or_buffer=path+'TFIDF',
                     index_col=['style', 'word'])
slab = normalized.loc['slab', 'tfidfn']

query = 'SELECT route_id, word, tfidfn FROM TFIDF WHERE route_id'
route = pd.read_sql(query, con=conn, index_col=['route_id', 'word'])

route = route.groupby('route_id').apply(cos_sim, b=slab)

print(route)

