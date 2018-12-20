# -*- coding: utf-8 -*-
"""
Created on Fri Dec 14 11:18:07 2018

@author: Bob
"""
import sqlite3
import numpy as np
import pandas as pd

pd.options.display.max_rows = 1000
pd.options.display.max_columns = 10000

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

ids = get_ids(slab)
cossims = np.array([[0.0] * len(ids)] * len(ids))

n = 1
for id1 in ids[:-1]:
    for id2 in ids[n:]:
        query = 'SELECT word, tfidfn FROM TFIDF WHERE route_id = %d' %id1
        idf = pd.read_sql(query, con=conn, index_col='word')
        idf = idf.rename(columns = {idf.columns[0]: 'A'})
        
        query2 = 'SELECT word, tfidfn FROM TFIDF WHERE route_id = %d' %id2
        idf2 = pd.read_sql(query2, con=conn, index_col='word')
        idf2 = idf2.rename(columns = {idf2.columns[0]: 'B'})
        
        tidf = pd.concat([idf, idf2], axis=1, join='inner', sort=True)
        tidf['t'] = tidf['A'] * tidf['B']
        cossim = cos_sim(tidf['A'], tidf['B'])
        cossim = round(cossim, 4)
        x = ids.index(id1)
        y = ids.index(id2)
        cossims[y][x] = cossim
    n += 1
    
cossims[cossims == 0] = np.nan
print(ids)
print(cossims)
print(np.nanmean(cossims))














