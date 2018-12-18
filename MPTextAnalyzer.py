# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 08:40:45 2018

@author: Bob
"""
import pandas as pd
import sqlite3
import numpy as np

conn = sqlite3.connect('Routes-Cleaned.sqlite')
cursor = conn.cursor()
    
def get_idf(word, num_docs):
    
    word['idf'] = 1 + np.log(num_docs / len(word))
    return word

def normalize(routes):
    length = np.sqrt(np.sum(routes['tfidf'] ** 2))
    routes['tfidfn'] = routes['tfidf'] / length
    return(routes)
    
def get_tfidf(min_occur=None, max_occur=None):
    cursor.execute('SELECT COUNT(route_id) FROM Routes WHERE tfidf = 1')
    num_docs = cursor.fetchone()[0]

    if min_occur == None:
        min_occur = 0.001 * num_docs
    if max_occur == None:
        max_occur = 0.9 * num_docs
        
    print('Finding words that appear in at least %d routes' % min_occur)
    print('Finding words that appear in no more than %d routes' % max_occur)
    print('Finding routes')
    query = 'SELECT route_id, word, tf FROM Words'
    print('Loading Pandas Frame')
    routes = pd.read_sql(query, con=conn, index_col=['route_id', 'word'])
    print('Sorting by word')
    routes = routes.groupby('word').apply(get_idf, num_docs=num_docs)
    print('Getting TFIDF values')
    routes['tfidf'] = routes['tf'] * routes['idf']
    print('Normalizing TFIDF values')
    routes = routes.groupby('route_id').apply(normalize)
    print('Commiting to SQL')
    routes.to_sql('IDF', con=conn, if_exists='replace')
    
    return routes

print(get_tfidf())