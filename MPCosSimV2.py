import pandas as pd
import re
import sqlite3
import numpy as np
import os
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import unidecode
    
path = os.getcwd()

conn = sqlite3.connect('Routes-Cleaned.sqlite')
cursor = conn.cursor()

pd.options.display.max_rows = 200000
pd.options.display.max_columns = 1000


def text_splitter(text):

    # Converts to lowercase
    text = text.lower()
    # Strips punctuation and converts accented characters to unaccented
    text = re.sub(r"[^\w\s']", '', text)
    text = unidecode.unidecode(text)
    # Tokenizes words and returns a list
    text = word_tokenize(text)
    # Stems each word in the list
    ps = PorterStemmer()
    text = [ps.stem(word) for word in text]
    
    return text


def normalize(*columns, table, inplace=False):
    for column in columns:
        if not inplace:
            column_name = column + 'n'
        elif inplace:
            column_name = column
        length = np.sqrt(np.sum(table[column] ** 2))
        table[column_name] = table[column] / length
    return table

def archetypal_tf(*styles, path):
    
    '''*styles are strings'''
    archetypes = pd.DataFrame()
    for style in styles:
        file = open(path + style + '.txt')
        text = ''
        for line in file:
            text += line
        text = text_splitter(text)
        length = len(text)
        text = pd.DataFrame({'word': text})['word']\
             .value_counts()\
             .rename('counts')\
             .to_frame()
        text[style] = text['counts'].values / length
        text = text[style]
        
        archetypes = pd.concat([archetypes, text], axis=1, sort=True)
    return archetypes

def archetypal_idf(words):
    query = '''SELECT DISTINCT(word), idf
               FROM TFIDF WHERE word IN {}'''.format(words)
    archetypes = pd.read_sql(query, con=conn, index_col='word')
    
    return archetypes

def archetypal_tfidf(idf, archetypes):
    tfidf = pd.DataFrame(idf.values * archetypes.values,
                         columns=archetypes.columns,
                         index=archetypes.index)
    tfidf.to_csv(path + 'TFIDF.csv')

    return tfidf 


def get_routes():
    query = '''SELECT route_id, word, tfidfn FROM TFIDF'''

    routes = pd.read_sql(query, con=conn, index_col=['route_id', 'word'])
    return routes.squeeze()

def cosine_similarity(route, archetypes):
    count = len(route)
    
    route.index = route.index.droplevel(0)
    archetypes = archetypes.multiply(route, axis=0)
    terrain = {'count': [count]}
    
    for column in archetypes:
        cosine = np.sum(archetypes[column])
        terrain[column] = [cosine]
        
    terrain = pd.DataFrame.from_dict(terrain)
    print(route.name, ' - ', count, 'words')
        
    return terrain
    
path += '\\Descriptions\\'

def score_routes():

    archetypes = archetypal_tf('arete', 'chimney', 'crack', 'slab','overhang',
                               path=path)
        
    words = tuple(archetypes.index.tolist())
    idf = archetypal_idf(words)
    archetypes = archetypes[archetypes.index.isin(idf.index)]
    
    archetypes = archetypal_tfidf(idf, archetypes)
    archetypes = normalize('arete', 'chimney', 'crack', 'slab', 'overhang',
                                table=archetypes, inplace=True)
    
    routes = get_routes().groupby('route_id').apply(cosine_similarity,
                                                    archetypes)
    routes.index = routes.index.droplevel(1)
    routes.to_sql('Terrain', con=conn, if_exists='replace')
    print(routes)
    
def temp_get_data():
    query = 'SELECT route_id, count, arete, chimney, crack, slab, overhang FROM Terrain'
    routes = pd.read_sql(query, con=conn, index_col = 'route_id')
    return routes

def weighted_scores(*columns, table, inplace=False):
    if inplace:
        count = 'count'
    else:
        count = 'count_norm'


    table[count] = 1 + np.log(table['count'])
    table[count] = table[count] / table[count].max() 
    

    for column in columns:
        if inplace:
            column_name = column
        else:
            column_name = column + '_weighted'

        max_val = table[column].max()
        column_avg = table[column].mean()

        table[column_name] = table[column] / max_val
        table[column_name] = ((table[column].values
                             * np.sqrt(table[column].values ** 2 
                                       + table[count].values ** 2))
                             + ((1 - table[count].values)
                             * (1 - table[column].values)
                             * column_avg))
        
        table[column_name] = table[column] / table[column].max()
         
    return table


routes = temp_get_data()
routes = weighted_scores('arete', 'chimney', 'crack', 'slab', 'overhang',
                         table=routes, inplace=True)
print(routes)
routes.to_sql('Terrain', con=conn, if_exists='replace')

