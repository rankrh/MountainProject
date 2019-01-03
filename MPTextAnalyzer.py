import numpy as np
import pandas as pd
import sqlite3

conn = sqlite3.connect('C:\\Users\\Bob\Documents\\Python\Mountain Project\\Routes-Cleaned.sqlite')
cursor = conn.cursor()

def idf(word, num_docs):
    print('Finding IDF for', word.name)

    word['idf'] = 1 + np.log(num_docs / len(word))
    return word

def normalize(routes):
    print('Normalizing TFIDF values for', routes.name)
    length = np.sqrt(np.sum(routes['tfidf'] ** 2))
    routes['tfidfn'] = routes['tfidf'] / length
    return routes['tfidfn'].to_frame()


def weed_out(table, min_occur, max_occur):
    if min_occur < len(table) < max_occur:
        return table.reset_index()
    
    
def tfidf(min_occur=None, max_occur=None):

    cursor.execute('SELECT COUNT(route_id) FROM Routes')
    num_docs = 1000 #cursor.fetchone()[0]

    if min_occur is None:
        min_occur = 0.001 * num_docs
    if max_occur is None:
        max_occur = 0.9 * num_docs
        
    # UPDATE TO COMBINE FUNCTIONS
    query = 'SELECT route_id, word, tf FROM Words LIMIT 1000'
    routes = pd.read_sql(query, con=conn, index_col='route_id')
    routes = routes.groupby('word')    
    routes = routes.apply(weed_out, min_occur, max_occur)
    routes = routes.groupby('word')    
    routes = routes.apply(idf, num_docs=num_docs)
    routes['tfidf'] = routes['tf'] * routes['idf']
    routes = routes.groupby('route_id').apply(normalize)
    return routes.head()
    routes.to_sql('TFIDF', con=conn, if_exists='replace')

    return routes

print(tfidf())