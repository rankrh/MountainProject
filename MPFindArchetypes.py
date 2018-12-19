# -*- coding: utf-8 -*-
"""
Created on Fri Dec 14 11:18:07 2018

@author: Bob
"""
import sqlite3
import numpy as np
import pandas as pd

pd.options.display.max_rows = 1000
pd.options.display.max_columns = 1000

conn = sqlite3.connect('Routes-Cleaned.sqlite')
cursor = conn.cursor()

folder = 'classic_routes/'
arete = [url.strip() for url in open(folder + 'arete.txt', 'r').readlines()]
chimney = [url.strip() for url in open(
        folder + 'chimney.txt', 'r').readlines()]
crack = [url.strip() for url in open(folder + 'crack.txt', 'r').readlines()]
face = [url.strip() for url in open(folder + 'face.txt', 'r').readlines()]
overhang = [url.strip() for url in open(
        folder + 'overhang.txt', 'r').readlines()]
vertical = [url.strip() for url in open(
        folder + 'vertical.txt', 'r').readlines()]
slab = [url.strip() for url in open(folder + 'slab.txt', 'r').readlines()]

styles = {'arete': arete, 'chimney': chimney, 'crack': crack, 'face': face,
          'overhang': overhang, 'vertical': vertical, 'slab': slab}

def get_ids(urls):
    ids = []
    for url in urls:
        cursor.execute('SELECT route_id FROM Routes WHERE url = ?', (url,))
        route_id = cursor.fetchone()[0]
        ids.append(route_id)
    return tuple(ids)


def cos_sim(a, b):
    dot_prod =  np.sum(a * b)
    return dot_prod

all_terrain = pd.DataFrame()
for style, routes in styles.items():
    rid = get_ids(routes)
    print(style)

    query = 'SELECT word, word_count FROM Words WHERE route_id IN ' + str(rid)
    terrain = pd.read_sql(query, con=conn).groupby('word')
    word_count = np.sum(terrain['word_count']).to_frame()
    total = int(np.sum(word_count))
    word_count['tf'] = word_count['word_count'] / total
    
    query = 'SELECT word, idf FROM IDF'
    idf = pd.read_sql(query, con=conn)
    
    word_count = pd.merge(word_count, idf, how='inner', on='word')
    word_count['tfidf'] =  word_count['tf'] * word_count['idf']
    length = np.sqrt(np.sum(word_count['tfidf'] ** 2))
    word_count['tfidfn'] = word_count['tfidf'] / length 
    word_count = word_count.set_index('word')['tfidfn']
    
    
    query = 'select word, route_id, tfidfn FROM TFIDFN'
    routes = pd.read_sql(query, con=conn, index_col='word').groupby('route_id')
    
    cossim = {}
    
    for route, word in routes:
        cossim[route] = [np.sum(word['tfidfn'] * word_count)]
    
    
    cossim = pd.DataFrame.from_dict(cossim, orient='index',
                                    columns = [style])
    cossim.index.rename('route_id')
    print(cossim.head())
    all_terrain = pd.concat([all_terrain, cossim], axis=1)



all_terrain.to_sql('Terrain', con=conn, if_exists='replace')