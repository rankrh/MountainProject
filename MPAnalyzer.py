# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 19:51:21 2018

@author: Bob
"""

import sqlite3
import pandas as pd
import os
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN


def MPAnalyzer(path='C:/Program\ Files/MountainProject/',
               DBname='MPRoutes'):
    # FIXME: Add Documentation


    try:
        os.mkdir(path)
    except OSError:
        message = "Creation of the directory %s failed" % path
        return message

    # Connect to SQLite database and create database 'Routes.sqlite'
    conn = sqlite3.connect(path + DBname + '.sqlite')
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
        epsilon = 0.007
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
        # FIXME: Add Documentation


        word['idf'] = 1 + np.log(num_docs / len(word))
        return word

    def normalize(routes):
        # FIXME: Add Documentation

        length = np.sqrt(np.sum(routes['tfidf'] ** 2))
        routes['tfidfn'] = routes['tfidf'] / length
        return(routes)

    def tfidf(min_occur=None, max_occur=None):
        # FIXME: Add Documentation

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
        routes.to_sql('IDF', con=conn, if_exists='replace')

        return routes

    def analyze_routes():
        # FIXME: Add Documentation

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

    tfidf(min_occur=0.001, max_occur=0.9)
    analyze_routes()

if __name__ == '__main__':
    MPAnalyzer(path='C:/Program\ Files/MountainProject/',
               DBname='MPRoutes')


# FIXME: See what else needs to be included for a __main__ file
