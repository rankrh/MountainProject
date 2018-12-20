# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 19:51:21 2018

@author: Bob
"""

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import pandas as pd
import numpy as np
import sqlite3
import os


def MPAnalyzer(path='C:/Users/', 
               folder='/Mountain Project',
               DBname='MPRoutes'):
    
    '''Finishes cleaning routes using formulas that require information about
    the whole database.

    The Bayesian rating system, route clustering algorithm and calculation of
    TFIDF values require information about all routes, and not just one that is
    of interest.  Therefore, this file must be run after all data collection
    has finished. This function is a handler for five functions:
        - bayesian_rating: Calculates the weighted quality rating for each
            route
        - route_clusters: Groups routes together based on geographic distance
        - idf: Calculates inverse-document-frequency for words in the route
            descriptions
        - tfidf: Calclates term-frequency-inverse-document-frequency for words
            in route descriptions
        - normalize: Normalizes vectors for TFIDF values

    Args:
        path(str): Location of the route database
        folder(str): Lower level location of the route database
    Returns:
        Updated SQL Database
    '''

    username = os.getlogin()
    if path == 'C:/Users/':
        path += username
    else:
        folder = ''

    try:
        os.chdir(path + folder)        
    except OSError as e:
        return e
    
    try:
        os.chdir(path + folder + '/Descriptions')
    except OSError as e:
        if e.winerror == 2:
            try:
                os.mkdir(path + folder + 'Descriptions')
                os.chdir(path + folder + 'Descriptions')
            except OSError as e:
                print(e)
                return e.winerror
        else:
            return e
        
    os.chdir(path + folder)        

    # Connect to SQLite database and create database 'Routes.sqlite'
    conn = sqlite3.connect(DBname + '.sqlite')
    # Create cursor
    cursor = conn.cursor()

    def bayesian_rating(routes):
        ''' Updates route quality with weighted average.

        The Bayesian average rating system helps to mitigate the effects of
        user ratings for routes that only have a few reviews.  The weighted
        rating works by first finding the average rating for all routes, and
        using that to bring low-rated routes up and high-rated routes down.
        Essentially, the function gives each route phantom-users who all give
        the route the average score.  For routes with a high number of ratings
        the effect of the additional phantom users is minimal, but for routes
        with only one or two actual user ratings, the effect is large.  This
        keeps 4-star rated routes from dominating the sorting algorithm if they
        only have a few votes, and helps promote unrated routes that may be
        quality.

        Args:
            routes(pandas df): Pulled from cleaned route SQL DB with columns:
                                - route_id (int, unique)
                                    Unique route identifiers
                                - stars (float)
                                    Raw average rating
                                - votes (int)
                                    Number of user ratings
        Returns:
            routes(pandas df): Updated dataframe with Bayes rating and columns:
                                - route_id (int, unique)
                                    Unique route identifies
                                - bayes (float)
                                    Weighted average rating
        '''
        # Average rating of all routes
        stars = pd.read_sql('SELECT stars FROM Routes', con=conn)
        avg_stars = np.mean(stars)['stars'] * 10

        # Weighted Bayesian rating
        routes['bayes'] = (((routes['votes'] * routes['stars']) + avg_stars) /
                            (routes['votes'] + 10))
        return routes['bayes'].to_frame()

    def route_clusters(routes):
        ''' Clusters routes into area groups that are close enough to travel
        between when finding climbing areas.

        Routes can be sorted into any number of sub-areas below the 'region'
        parent. By clustering the routes based on latitude and longitude
        instead of the name of the areas and parent areas, the sorting
        algorithm will be able to more accurately determine which routes are
        close together. This function uses SciKit's Density Based Scan
        clustering algorithm. The algorithm works by grouping points together
        in space based on upper-limits of distance and minimum numbers of
        members of a cluster. More generally, the algorithm first finds the
        epsilon neighborhood of a point. This is the set of all points whose
        distance from a given point is less than a specified value epsilon.
        Then, it finds the connected core-points, which are the points that
        have at least the minimum number of connected points in its
        neighborhood. Non-core points are ignored here.  Finally, the
        algorithm assigns each non-core point to a nearby cluster if is within
        epsilon, or assigns it to noise if it is not.

        The advantages of this is that the scan clusters data of any shape, has
        a robust response to outliers and noise, and that the epsilon and min
        points variables can be adjusted.

        This function returns the label/name for the cluster that a route
        appears in, as well as the number of other routes in that same cluster.
        This will allow the sorting algorithm to more heavily weight routes
        that are clustered near others.


        Args:
            routes(pandas df): Pulled from cleaned route SQL DB with columns:
                                - route_id (int, unique)
                                    Unique route identifies
                                - latitude (float)
                                - longitude (float)
        Returns:
            routes(pandas df): Updated with clustered area group number
                                - route_id (int, unique)
                                    Unique route identifies
                                - area_group (int)
                                    Cluster id
                                - area_counts (int)
                                    Number of routes in cluster
        '''
        # Route location

        lats = routes['latitude']
        longs = routes['longitude']
        locs = []
        for x in range(len(lats)):
            locs.append((lats.iloc[x], longs.iloc[x]))

        # Converted into df
        locs = StandardScaler().fit_transform(locs)
        # Max distance in latitude
        epsilon = 0.0007
        # Min number of routes in a cluster
        min_routes = 3
        # Distance baced scan
        db = DBSCAN(eps=epsilon, min_samples=min_routes).fit(locs)
        core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
        core_samples_mask[db.core_sample_indices_] = True
        # Cluster names
        labels = db.labels_
        unique, counts = np.unique(labels, return_counts=True)
        counts = dict(zip(unique, counts))
        # Number of routes in the same cluster as a given route
        area_counts = []
        # Find area clusters
        for label in labels:
            if label >= 0:
                # Counts number of routes
                area_counts.append(counts[label])
            # Areas are given a cluster id of -1 if the are not part of a
            # cluster
            elif label == -1:
                # If so, there is only 1 route in their 'cluster'
                area_counts.append(1)

        routes['area_group'] = labels
        routes['area_counts'] = area_counts
        routes = routes[['area_group', 'area_counts']]
        return routes

    def idf(word, num_docs):
        ''' Findes inverse document frequency for each word in the selected
        corpus.

        Inverse document frequency(IDF) is a measure of how often a word appears in
        a body of documents.  The value is calculated by:

                            IDF = 1 + log(N / dfj)
    
            Where N is the total number of documents in the corpus and dfj is
        the document frequency of a certain word, i.e., the number of documents
        that the word appears in.

        Args:
            word(pandas dataframe): A dataframe composed of all instances of a
                word in a corpus.
            num_docs(int): The total number of documents in the corpus

        Returns:
            word(pandas dataframe): The same document with the calculated
                IDF score appended.
        '''

        word['idf'] = 1 + np.log(num_docs / len(word))
        return word

    def normalize(routes):
        ''' Normalizes vector length.
        
        TFIDF values must be normalized to a unit vector to control for
        document length.  This process is done by calculating the length of the
        vector and dividing each term by that value.  The resulting
        'unit-vector' will have a length of 1.

        Args:
            routes(pandas dataframe): The TFIDF scores for a word connected to
                its route_id.

        Returns:
            routes(pandas dataframe): The same dataframe with an appended
                column for nomalized TFIDF values.
        '''
        
        length = np.sqrt(np.sum(routes['tfidf'] ** 2))
        routes['tfidfn'] = routes['tfidf'] / length
        return routes

    def tfidf(min_occur=None, max_occur=None):
        ''' Calculates Term-Frequency-Inverse-Document-Frequency for a body of
        documents.
        
        Term-Frequency-Inverse-Document-Frequency(TFIDF) is a measure of the
        importance of words in a body of work measured by how well they help to
        distinguish documents.  Words that appear frequently in documents score
        high on the Term-Frequency metric, but if they are common across the
        corpus, they will have low Inverse-Document-Frequency scores.  TFIDF
        can then be used to compare documents to each other, or, in this case,
        to documents with known topics.
        
        Args:
            min_occur(int): The minimum number of documents that a word has to
                appear in to be counted. Included to ignore words that only
                appear in a few documents, and are therefore not very useful
                for categorization.
            max_occur(int): The maximum number of documents that a word can
                appear in to be counted.  This is included to ignore highly
                common words that don't help with categorization.
                
        Returns:
            routes(pandas Dataframe): Holds route-document information,
                including term-frequency, inverse-document-frequency, TFIDF,
                and normalized TFIDF values
            Updated SQL Database: Updates the TFIDF table on main DB with the
                routes dataframe
        '''

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
    
    def archetype_tfidf():
        # FIXME: Add Documentation
        try:
            os.chdir(path + folder + '/Descriptions')
        except OSError as e:
            if e.winerror == 2:
                try:
                    os.mkdir(path + folder + 'Descriptions')
                    os.chdir(path + folder + 'Descriptions')
                except OSError as e:
                    print(e)
                    return e.winerror
            else:
                return e
        
        def archetype_idf(word, idf):
        # FIXME: Add Documentation
            try:
                val = idf.loc[word.name]['idf']
                word['idf'] = val
                word['tfidf'] = word['tf'] * word['idf']
                return word
                
            except KeyError:
                print(word.name, end=' ')
                print('Not in idf DF')
                
        def archetype_tf(path):
        # FIXME: Add Documentation
            archetypes = pd.DataFrame()
            names = ['arete', 'chimney', 'crack', 'slab', 'overhang', 'face']
            
            for name in names:    
                 tf = pd.read_csv(filepath_or_buffer=path + name)
                 tf = tf.rename(columns={tf.columns[0]: 'word'})
                 tf['style'] = name
                 tf = tf.set_index(['style', 'word'])
                 archetypes = pd.concat([archetypes, tf])

        def cos_sim(a, b):
            #FIXME: What is the best way to get cossim for an arbitrary number
            # of different styles that can be added to without forcing me to 
            # circle back around OR to go back here and adjust the number of arguments?
            # FIXME: Add Documentation
            print(a.name)
            dot_prod =  np.sum(a['tfidfn'] * b)
            return dot_prod

        
        archetypes = archetype_tf(path)
        
        unique = archetypes.index.levels[1].unique().tolist()
        unique = tuple(unique)
        query = 'SELECT DISTINCT(word), idf from TFIDF WHERE word IN {}'.format(unique)
        idf = pd.read_sql(query, con=conn, index_col='word')
         
        archetypes = archetypes.groupby(level=[1]).apply(archetype_idf,
                                        idf=idf)
        archetypes = archetypes.reset_index(level=0, drop=True)
        
        archetypes = archetypes.groupby('style').apply(normalize)
        
        arete = archetypes.loc['arete', 'tfidfn']
        chimney = archetypes.loc['chimney', 'tfidfn']
        crack = archetypes.loc['crack', 'tfidfn']
        slab = archetypes.loc['slab', 'tfidfn']
        overhang = archetypes.loc['overhang', 'tfidfn']
        face = archetypes.loc['face', 'tfidfn']
        
    
        
        


    
    
        
    tfidf(min_occur=0.001, max_occur=0.6)

    cluster_text = '''SELECT route_id, latitude, longitude
                      FROM Routes'''
    clusters = pd.read_sql(cluster_text, con=conn, index_col='route_id')
    clusters = route_clusters(clusters)

    bayes_text = '''SELECT route_id, stars, votes
                    FROM Routes'''
    bayes = pd.read_sql(bayes_text, con=conn, index_col='route_id')
    bayes = bayesian_rating(bayes)

    add = pd.concat([bayes, clusters], axis=1)

    for route in add.index:
        rate = add.loc[route]['bayes']
        group = add.loc[route]['area_group']
        cnt = add.loc[route]['area_counts']

        cursor.execute('''UPDATE Routes
                         SET bayes = ?, area_group = ?, area_counts = ?
                         WHERE route_id = ?''', (rate, group, cnt, route))
    conn.commit()


if __name__ == '__main__':
    print(MPAnalyzer())
