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
    names = ['arete', 'chimney', 'crack', 'slab', 'overhang']
    
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
    return archetypes

def normalize(routes):
    
    length = np.sqrt(np.sum(routes['tfidf'] ** 2))
    routes['tfidfn'] = routes['tfidf'] / length
    return routes


def get_tfidfn():
    normalize(tfidf_values())

    styles = pd.read_csv(filepath_or_buffer=path+'TFIDF',
                         index_col=['style', 'word'])
    styles = styles.groupby('style').apply(normalize).sort_index(level=[0, 1])
    styles.to_csv(path + 'TFIDF')
    
    
def cos_sim(route, styles):
    global terrain_data
    terrain = pd.DataFrame(index=[route.name], columns = list(styles.keys()))
    for style, data in styles.items():
        dot_prod = np.sum(data * route)
        terrain[style] = dot_prod
    terrain_data = pd.concat([terrain_data, terrain])
    if route.name % 100 == 0:
        print(terrain_data)
        terrain_data.to_sql('Terrain', con=conn, if_exists='append', index_label='route_id')
        terrain_data = pd.DataFrame()
        

def get_terrain(normalized):
    arete = normalized.loc['arete']
    chimney = normalized.loc['chimney']
    crack = normalized.loc['crack']
    slab = normalized.loc['slab']
    overhang = normalized.loc['overhang']
    #face = normalized.loc['face']
    
    styles = {'arete': arete, 'chimney': chimney, 'crack': crack,
              'slab': slab, 'overhang': overhang} #, 'face': face}
    
    
    query = '''SELECT route_id, word, tfidfn
               FROM TFIDF
               WHERE route_id
               NOT IN (SELECT route_id FROM Terrain)'''
    
    routes = pd.read_sql(query, con=conn, index_col=['route_id', 'word'])
        
    routes = routes['tfidfn'].groupby('route_id').apply(cos_sim, styles)
    
    terrain_data.to_sql('Terrain', con=conn, if_exists='append', index_label='route_id')
    
    
    #print(route)
terrain_data = pd.DataFrame()

def get_data():
    
    normalized = pd.read_csv(filepath_or_buffer=path+'TFIDF.csv',
                         index_col=['style', 'word'])['tfidfn']
    get_terrain(normalized)
    

def normalize_cossim():
    routes = pd.read_sql('SELECT * FROM Terrain',
                         con=conn,
                         index_col='route_id')
    routes['arete_norm'] = routes['arete'].values / routes['arete'].max()
    routes['chimney_norm'] = routes['chimney'].values / routes['chimney'].max()
    routes['crack_norm'] = routes['crack'].values / routes['crack'].max()
    routes['slab_norm'] = routes['slab'].values / routes['slab'].max()
    routes['overhang_norm'] = routes['overhang'].values / routes['overhang'].max()
    
    return routes[['arete_norm', 'chimney_norm', 'crack_norm',
                   'slab_norm', 'overhang_norm']]
    
def get_word_count():
    raw = pd.read_sql('SELECT route_id, word_count FROM Words',
                      con=conn,
                      index_col='route_id').groupby(level=0)\
                      .apply(lambda x: np.sum(x))
    raw['log'] = 1 + np.log(raw['word_count'])
    raw_max = raw['log'].max()
    raw['count_normal'] = raw['log'] / raw_max
    return raw['count_normal']

   
routes = normalize_cossim()
count = get_word_count()

routes = pd.concat([routes, count], axis=1, sort=False)

avg_arete = routes['arete_norm'].mean()
avg_chim = routes['chimney_norm'].mean()
avg_crack = routes['crack_norm'].mean()
avg_slab = routes['slab_norm'].mean()
avg_overhang = routes['overhang_norm'].mean()

routes['arete_score'] = (routes['arete_norm'].values
                         * np.sqrt(routes['count_normal'].values ** 2
                                   + routes['arete_norm'].values ** 2) 
                         + ((1 - routes['count_normal']) 
                         * (1 - routes['arete_norm']) * avg_arete))

routes['chimney_score'] = (routes['chimney_norm'].values
                           * np.sqrt(routes['count_normal'].values ** 2
                                     + routes['chimney_norm'].values ** 2)
                           + ((1 - routes['count_normal'])
                           * (1 - routes['chimney_norm']) * avg_chim))

routes['crack_score'] = (routes['crack_norm'].values
                         * np.sqrt(routes['count_normal'].values ** 2
                                   + routes['crack_norm'].values ** 2)
                         + ((1 - routes['count_normal'])
                         * (1 - routes['crack_norm']) * avg_crack))

routes['slab_score'] = (routes['slab_norm'].values
                        * np.sqrt(routes['count_normal'].values ** 2
                                  + routes['slab_norm'].values ** 2)
                        + ((1 - routes['count_normal'])
                        * (1 - routes['slab_norm']) * avg_slab))

routes['overhang_score'] = (routes['overhang_norm'].values
                            * np.sqrt(routes['count_normal'].values ** 2
                                      + routes['overhang_norm'].values ** 2)
                            + (1 - routes['count_normal'])
                            * (1 - routes['overhang_norm']) * avg_overhang)

max_arete = routes['arete_score'].max()
max_chimney = routes['chimney_score'].max()
max_crack = routes['crack_score'].max()
max_slab = routes['slab_score'].max()
max_overhang = routes['overhang_score'].max()

routes['arete'] = routes['arete_score'].values / max_arete
routes['chimney'] = routes['chimney_score'].values / max_chimney
routes['crack'] = routes['crack_score'].values / max_crack
routes['slab'] = routes['slab_score'].values / max_slab
routes['overhang'] = routes['overhang_score'].values / max_overhang

routes = routes[['arete', 'chimney', 'crack', 'slab', 'overhang']]

routes.to_sql('Scores', con=conn, if_exists='replace')

query = '''SELECT route_id, url FROM Routes
           WHERE route_id IN 
           (SELECT route_id FROM Scores ORDER BY chimney DESC LIMIT 10)'''

urls = pd.read_sql(query, con=conn)

for url in urls['url']:
    print(url)
    
print(urls['route_id'])
           
           

