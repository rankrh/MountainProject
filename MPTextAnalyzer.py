import numpy as np
import pandas as pd
import sqlite3

conn = sqlite3.connect('Routes-Cleaned.sqlite')
cursor = conn.cursor()

def idf(word, num_docs):
    print('Finding IDF for', word)

    word['idf'] = 1 + np.log(num_docs / len(word))
    return word

def normalize(routes):
    print('Normalizing TFIDF values for', routes)
    length = np.sqrt(np.sum(routes['tfidf'] ** 2))
    routes['tfidfn'] = routes['tfidf'] / length
    return routes['tfidfn'].to_frame()

def tfidf(min_occur=None, max_occur=None):

    cursor.execute('SELECT COUNT(route_id) FROM Routes')
    num_docs = cursor.fetchone()[0]

    if min_occur is None:
        min_occur = 0.001 * num_docs
    if max_occur is None:
        max_occur = 0.9 * num_docs

    query = 'SELECT route_id, word, tf FROM Words'
    routes = pd.read_sql(query, con=conn, index_col=['route_id', 'word'])
    routes = routes.groupby('word').apply(idf, num_docs=num_docs)
    routes['tfidf'] = routes['tf'] * routes['idf']
    routes = routes.groupby('route_id').apply(normalize)
    routes.to_sql('TFIDF', con=conn, if_exists='replace')

    return routes

tfidf()