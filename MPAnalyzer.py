# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 19:51:21 2018

@author: Bob
"""

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from sqlalchemy import create_engine
from config import config
import pandas as pd
import numpy as np
import unidecode
import psycopg2
import os
import re

def MPAnalyzer():
    '''Finishes cleaning routes using formulas that require information about
    the whole database.

    The Bayesian rating system, route clustering algorithm and calculation of
    TFIDF values require information about all routes, and not just one that is
    of interest.  Therefore, this file must be run after all data collection
    has finished. This function is a handler for six functions:
        - bayesian_rating: Calculates the weighted quality rating for each
            route
        - route_clusters: Groups routes together based on geographic distance
        - idf: Calculates inverse-document-frequency for words in the route
            descriptions
        - tfidf: Calclates term-frequency-inverse-document-frequency for words
            in route descriptions
        - normalize: Normalizes vectors for TFIDF values
        - find_route_styles: Compares routes to the ideal to help categorize

    Args:
        path(str): Location of the route database
        folder(str): Lower level location of the route database
    Returns:
        Updated SQL Database
    '''

    params = config.config()
    print('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect(**params)
    # Create cursor
    cursor = conn.cursor()
    cursor.execute('SELECT version()')
    db_version = cursor.fetchone()
    print([version for version in db_version])

    engine = create_engine('postgresql://postgres:postgres@localhost:5432/routes')

    def bayesian_rating(routes):
        ''' Updates route quality with weighted average.

        The Bayesian average rating system helps to mitigate the effects of
        user ratings for routes that only have a few reviews.  The weighted
        rating works by first finding the average rating for all routes, and
        using that to bring low-rated routes up and high-rated routes down.
        The result - the Bayes rating - is an updated rating weighted by the
        average number of stars across all routes.  The weight decreases
        according to the number of votes cast.

                Bayesian rating = (r * v) + (a * 10) / (v + 10)

                    s = Route rating
                    v = Number of votes
                    a = Average rating across all routes

        Essentially, the function gives each route phantom-users who all give
        the route the average score.  For routes with a high number of ratings
        the effect of the additional phantom users is minimal, but for routes
        with only one or two actual user ratings, the effect is large.  This
        keeps 4-star rated routes from dominating the sorting algorithm if they
        only have a few votes, and helps promote unrated routes that may be of
        high quality.

        Args:
            routes(pandas df): Pulled from cleaned route SQL DB with columns:
                - route_id (int, unique): Unique route identifiers
                - stars (float): Raw average rating
                - votes (int): Number of user ratings
        Returns:
            routes(pandas df): Updated dataframe with Bayes rating and columns:
                - route_id (int, unique): Unique route identifies
                - bayes (float): Weighted average rating
        '''

        # Average rating of all routes
        stars = pd.read_sql('SELECT stars FROM Routes', con=conn)
        avg_stars = np.mean(stars)['stars']
        # Weighted Bayesian rating
        routes['bayes'] = (((routes['votes'] * routes['stars'])
                            + avg_stars * 10) / (routes['votes'] + 10))
        return routes['bayes'].to_frame()
    
    def fill_null_loc():
        """Fills empty route location data.
        
        Not all routes have latitude and longitude coordinates, so we must use
        the coordinates of their parent area instead as a rough estimate.  This
        function first grabs all routes with no data, then fills in the data
        with the lowest level area it can, going up as many areas as needed
        until it finds one with proper coordinates.
        
        Returns:
            Updated SQL Database
            """
        # Select a route without location data
        cursor.execute('''
            SELECT route_id, area_id, name FROM Routes
            WHERE latitude is Null OR longitude is Null
            LIMIT 1''')
        route = cursor.fetchone()
        
        while route is not None:
            # Route ID
            rid = route[0]
            # From ID
            fid = route[1]
            name = route[2]
            print('Processing:', name)
    
            # Loops until it finds proper data
            lat, long = None, None
            while lat == None or long == None:
                # Gets latitude and longitude from parent area
                cursor.execute('''
                    SELECT latitude, longitude, from_id
                    FROM Areas
                    WHERE id = %s''', % (fid,))
                loc = cursor.fetchone()
                lat, long = loc[0], loc[1]
                fid = loc[2]
            # Updates DB
            cursor.execute('''
                UPDATE Routes
                SET latitude = %s, longitude = %s
                WHERE route_id = %s''', % (lat, long, rid))
            conn.commit()
            cursor.execute('''
                SELECT route_id, area_id, name
                FROM Routes WHERE latitude is Null OR longitude is Null
                LIMIT 1''')
            route = cursor.fetchone()
        return 'Done'    


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
                - route_id (int, unique): Unique route identifies
                - latitude (float)
                - longitude (float)
        Returns:
            routes(pandas df): Updated with clustered area group number:
                - route_id (int, unique): Unique route identifies
                - area_group (int): Cluster id
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

        routes['area_group'] = labels
        routes = routes['area_group']
        return routes

    def idf(word, num_docs):
        ''' Findes inverse document frequency for each word in the selected
        corpus.

        Inverse document frequency(IDF) is a measure of how often a word
        appears in a body of documents.  The value is calculated by:

                            IDF = 1 + log(N / dfj)

             N = Total number of documents in the corpus
             dfj = Document frequency of a certain word, i.e., the number of
                 documents that the word appears in.

        Args:
            word(pandas dataframe): A dataframe composed of all instances of a
                word in a corpus.
            num_docs(int): The total number of documents in the corpus

        Returns:
            word(pandas dataframe): The same document with the calculated IDF
                score appended.
        '''

        word['idf'] = 1 + np.log(num_docs / len(word))
        return word.reset_index()

    def normalize(*columns, table, inplace=False):
        ''' Normalizes vector length.

        Vector values must be normalized to a unit vector to control for
        differences in length.  This process is done by calculating the length
        of a vector and dividing each term by that value.  The resulting
        'unit-vector' will have a length of 1.

        Args:
            table(pandas dataframe): Table hosting vector to be normalized
            *columns(str): Names of columns to be normalized
            inplace(Boolean, default = False):
                If inplace=False, adds new columns with normalized values.
                If inplace=True, replaces the columns.

        Returns:
            table(pandas dataframe): Updated dataframe with normalized values.
        '''
        for column in columns:
            if not inplace:
                column_name = column + 'n'
            elif inplace:
                column_name = column

            length = np.sqrt(np.sum(table[column] ** 2))
            table[column_name] = table[column] / length
        return table.reset_index()


    def weed_out(table, min_occur, max_occur):
        if min_occur < len(table) < max_occur:
            return table.reset_index()


    def tfidf(min_occur=0.001, max_occur=0.9):
        ''' Calculates Term-Frequency-Inverse-Document-Frequency for a body of
        documents.

        Term-Frequency-Inverse-Document-Frequency(TFIDF) is a measure of the
        importance of words in a body of work measured by how well they help to
        distinguish documents.  Words that appear frequently in documents score
        high on the Term-Frequency metric, but if they are common across the
        corpus, they will have low Inverse-Document-Frequency scores.  TFIDF
        can then be used to compare documents to each other, or, in this case,
        to documents with known topics.

                                   TFIDF = TF * IDF

                          TF = Term Frequency
                          IDF = Inverse Document Frequency

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

        print('Getting number of routes...........', end=' ')
        cursor.execute('SELECT COUNT(route_id) FROM Routes')
        num_docs = cursor.fetchone()[0]
        print(num_docs)
        
        min_occur *= num_docs
        max_occur *= num_docs

        print('Getting route text data............', end=' ')
        query = 'SELECT route_id, word, tf FROM Words'
        routes = pd.read_sql(query, con=conn, index_col='route_id')
        print('Done')
        routes = routes.groupby('word', group_keys=False)
        print('Removing non-essential words.......', end=' ')
        routes = routes.apply(weed_out, min_occur, max_occur)\
                       .set_index('route_id')
        print('Done')
        routes = routes.groupby('word', group_keys=False)
        print('Getting IDF........................', end=' ')
        routes = routes.apply(idf, num_docs=num_docs).set_index('route_id')
        print('Done')        
        print('Calculating TFIDF..................', end=' ')
        routes['tfidf'] = routes['tf'] * routes['idf']
        print('Done')
        routes = routes.groupby(routes.index, group_keys=False)
        print('Normalizing TFIDF values...........', end=' ')
        routes = routes.apply(lambda x: normalize('tfidf', table=x))
        print('Done')
        routes = routes.set_index('route_id')
        print('Writing to SQL.....................', end=' ')
        routes.to_sql('TFIDF_TEST', con=conn, if_exists='replace')
        print('Done')

        return routes

    def find_route_styles(*styles, path):
        ''' Returns weighted scores that represent a route's likelihood of
        containing any of a series of features, e.g., a roof, arete, or crack.
    
        Route names, descriptions, and user comments can indicate the presence
        of rock and route features. Term-Frequency-Inverse-Document-Frequency
        (TFIDF) values for the blocks of text gathered for each route can be
        compared to 'archetypal' routes to glean insight into these features.
        This comparison is further clarified using Bayesian statistics to
        measure the credibility of the comparision, and is then adjusted to
        reflect that.  At present, each route is compared against archetypal
        routes with the following features:
    
            Aretes - A sharp vertical edge of a block, cliff or boulder
            Chimney - A large vertical crack that a climber can fit in and
                climb using opposing pressure
            Crack - Smaller cracks ranging from finger-sized to a few inches
                wide (off-width)
            Slab - Low-angle rock faces (less than vertical)
            Overhang - Roofs, caves or more-than-vertical rock faces
    
        More styles or archetypes can be added in the future by creating .txt
        files and adding them to the 'Descriptions' sub-folder, then adding the
        style to the *styles argument.
    
        Args:
            *styles(str): The name of the files that each route will be
                compared against.
            path(str): Folder location of the Database
    
        Returns:
            Updated SQL Database with weighted route scores
        '''
    
        def text_splitter(text):
            '''Splits text into words and removes punctuation.
    
            Once the text has been scraped it must be split into individual
            words for further processing.  The text is all put in lowercase,
            then stripped of punctuation and accented letters. Tokenizing helps
            to further standardize the text, then converts it to a list of
            words. Each word is then stemmed using a Porter stemmer.  This
            removes suffixes that make similar words look different, turning,
            for example, 'walking' or 'walked' into 'walk'.  Stop words are
            also filtered out at this stage.
    
            Args:
                text(str): Single string of text to be handled
    
            Returns:
                text(list): List of processed words.'''
    
            # Converts to lowercase
            text = text.lower()
            # Strips punctuation and converts accented characters to unaccented
            text = re.sub(r"[^\w\s']", '', text)
            text = unidecode.unidecode(text)
            # Tokenizes words and returns a list
            text = word_tokenize(text)
            # Remove stopwords            
            stop_words = set(stopwords.words('english'))
            # Stems each word in the list
            ps = PorterStemmer()
            text = [ps.stem(word) for word in text if word not in stop_words]
    
            return text
    
        def archetypal_tf(*styles, path):
            ''' Returns term-frequency data for descriptions of archetypal
            climbing routes and styles.  This will be used later to categorize
            routes.
    
                            Term-Frequency = t / L
    
                    t = Number of appearances for a word in a document
                    L = Number of total words in the document
    
            Args:
                *styles(str): Name of .txt file to parse.  Can either be the
                    plain name or have the .txt suffix
                path(str): Path to folder with route descriptions
            Returns:
                tf.csv(CSV File): CSV File of term frequency for each style.
                    This will help determine if TF values are what is expected
                    when adding new styles.
                archetypes(Pandas Dataframe): Holds words term-frequency values
                    for words in the files.'''
    
            # Initializes Dataframe
            archetypes = pd.DataFrame()
            for style in styles:
                # Formats suffix
                if style.endswith('.txt'):
                    # Opens .txt file
                    try:
                        file = open(path + style)
                        style = style[:-4]
                    # Returns errors
                    except OSError as e:
                        return e
                else:
                    try:
                        file = open(path + style + '.txt')
                    except OSError as e:
                        return e
    
    
                # Creates single block of text
                text = ''
                for line in file:
                    text += line
                # Splits and processes text
                text = text_splitter(text)
    
                # Length of document in words
                length = len(text)
                # Counts appearances of each word
                text = pd.DataFrame({'word': text})['word']\
                         .value_counts()\
                         .rename('counts')\
                         .to_frame()
    
                # Calculates Term-Frequency
                text[style] = text['counts'].values / length
                text = text[style]
    
                # Creates master Dataframe of Termfrequency data for each style
                archetypes = pd.concat([archetypes, text], axis=1, sort=True)
            archetypes.to_csv(path + 'TF.csv')
            return archetypes
    
        def archetypal_idf(words):
            ''' Findes inverse document frequency (IDF) for each word in the
            archetypal style documents.
    
            The archetypal documents should not be included in the calculation
            of IDF values, so this function just pulls the IDF values from the
            database after they are calculated. IDF is a measure of how often a
            word appears in a body of documents. The value is calculated by:
    
                                IDF = 1 + log(N / dfj)
    
                 N = Total number of documents in the corpus
                 dfj = Document frequency of a certain word, i.e., the number
                     of documents that the word appears in.
    
            Args:
                word(list): All unique words in all the archetype documents
    
            Returns:
                archetypes(pandas dataframe): IDF values for each word pulled
                    from the Database.'''
    
            # Formats query to include list of unique words
            query = '''SELECT DISTINCT(word), idf
                       FROM TFIDF WHERE word IN {}'''.format(words)
            # Pulls SQL data into Pandas dataframe
            archetypes = pd.read_sql(query, con=conn, index_col='word')
    
            return archetypes
    
        def get_routes(route_ids=None):
            '''Creates Pandas Dataframe of normalized TFIDF values for each
            word in each route description.
    
            Args:
            Returns:
                routes(Pandas Series): MultiIndex series with indexes
                'route_id' and 'word' and column 'tfidfn' - Normalized TFIDF'''
    
            # Pulls route_id, word, and normalized TFIDF value
            if route_ids is None:
                query = 'SELECT route_id, word, tfidfn FROM TFIDF'
            else:
                route_ids = tuple(route_ids)
                query = '''SELECT route_id, word, tfidfn FROM TFIDF
                           WHERE route_id in {}'''.format(route_ids)
    
            # Creates Pandas Dataframe
            routes = pd.read_sql(query,
                                 con=conn,
                                 index_col=['route_id', 'word'])
    
            # Converts to series
            routes = routes.squeeze()
            return routes
    
        def get_word_count(route_ids=None):
            '''Finds length of route description in words.
    
            Args:
            Returns:
                word_count(Pandas dataframe): Dataframe with index route_id and
                    column 'word_count' - length of a route description in
                    words'''
    
            # Pulls route_id and word_count for each route
            if route_ids is None:
                query = 'SELECT route_id, word_count FROM Words'
            else:
                route_ids = tuple(route_ids)
                query = '''SELECT route_id, word_count FROM Words
                           WHERE route_id in {}'''.format(route_ids)
    
            # Calculates document length
            word_count = pd.read_sql(query,
                                     con=conn,
                                     index_col='route_id').groupby(level=0)

            # We will take the log of the word count later, so we cannot leave
            # zeroes in the series
            word_count = word_count.apply(lambda x: np.sum(x) + 0.01)
            word_count.fillna(0.01, inplace=True)
            
            return word_count
    
        def cosine_similarity(route, archetypes):
            '''Compares routes to archetypes to help categorize route style.
    
            Cosine similarity is the angle between two vectors.  Here, the
            normalized TFIDF values for each word in the route description and
            archetype documents serve as the coordinates of the vector. Finding
            the cosine similarity is therefore simply their dot-product.
    
                    Cosine Similarity = Σ(ai * bi)
    
                    ai = TFIDF for a word in the route description
                    bi = TFIDF for the same word in the archetype document.
    
            The similarity will range between 0 and 1, 1 being identical and 0
            having no similarity.
    
            Args:
                route(Pandas dataframe): MultiIndex frame with indexes route_id
                    and word and columns normalized TFDIF values
                archetypes(Pandas dataframe): Frame with index word and columns
                    normalized TFIDF values.
    
            Returns:
                terrain(Pandas dataframe): Frame with columns for each style,
                    holding cosine simlarity values.'''
    
            # Removes the route_id level of the multiindex
            route.index = route.index.droplevel(0)
            # Multiplies the route TFIDF values by each column of the
            # archetypes frame
            archetypes = archetypes.multiply(route, axis=0)
    
            # Initiates dictionary that will hold the cosine similarity for
            # each style
            terrain = {}
            for column in archetypes:
                # Sums the vector and passes it into the dictionary
                cosine = np.sum(archetypes[column])
                terrain[column] = [cosine]
    
            # Creates dataframe from the dictionary
            terrain = pd.DataFrame.from_dict(terrain)
            # Updates user
            print('    Scoring route''', route.name)
    
            return terrain
    
        def score_routes(*styles, word_count, path, routes):
            '''Gets TF, IDF data for archetypes, then finds TFIDF and cosine
            similarity for each route/style combination.
    
            Finding the raw cosine similarity scores requires the functions
            archetypal_tf, archetypal_idf, and normalize.  This function helps
            organize the retrieval and processing of the data for those functions.
    
            Args:
                word_count(Pandas dataframe): Dataframe with index route_id and
                    column 'word_count' - length of a route description in
                    words
            Returns:
                TFIDF.csv(CSV file): TFIDF for each word in each style.  This
                    helps users determine if the TFIDF values are what they
                    would expect when adding new styles.
                routes(Pandas dataframe): Holds cosine similarity for each
                    route/style combination'''
    
            # Gets Term-Frequency data for words in archetype documents
            archetypes = archetypal_tf(*styles, path=path)
            # Gets list of unique words in archetype documents
            words = tuple(archetypes.index.tolist())
            # Gets IDF Values for those words from the Database
            idf = archetypal_idf(words)
            # Selects words for archetype documents that have a correpsonding
            # IDF value in the database
            archetypes = archetypes[archetypes.index.isin(idf.index)]
    
            # Multiplies TF by IDF values to get TFIDF score
            archetypes = archetypes.mul(idf['idf'], axis=0)
            # Normalizes TFIDF scores
            archetypes = normalize(table=archetypes,
                                   inplace=True,
                                   *styles)
            archetypes = archetypes.rename(columns={'index': 'word'})\
                                   .set_index('word')
            # Writes to CSV
            archetypes.to_csv(path + 'TFIDF.csv')
    
            # Groups words by route_id, then finds cosine similarity for each
            # route-style combination
            routes = routes.groupby('route_id').apply(cosine_similarity,
                                                      archetypes)
            # Reformats routes dataframe
            routes.index = routes.index.droplevel(1)
            routes = pd.concat([routes, word_count], axis=1, sort=False)
            routes.fillna(0, inplace=True)
    
            return routes
    
        def weighted_scores(*styles, table, inplace=False):
            '''Weights cosine similarity based on credibility.
    
            The cosine similarity between a route and a style archetype
            measures how close the two documents are.  Depending on the score
            and the word count of the route, however, this score can be more or
            less believable.  Using Bayesian statistics helps weight the scores
            based on the credibility.
    
            We can plot word count and cosine similarity in two dimensions.
            Normalizing each so that the maximum value is one results in a
            plane with four edge cases:
    
                            cosine similarity | word count
                                    0               0
                                    1               0
                                    0               1
                                    1               1
    
            (Note: We will actually take the log of the word count. The law of
            diminishing returns applies in this case.)
    
            When both word count and cosine similarity is high, the
            believability of the cosine score is at its highest.  This is
            analagous to a route that scores well with the 'overhang' document,
            therefore mentioning words like 'overhang' or 'roof' frequently,
            that also has a lot of words.
    
            If the word count is high and the cosine similarity is low the
            believability of the score is high, but not as high as before.
            This is analagous to a route that never mentions words associated
            with 'overhang' despite a high word count.  We can be reasonably
            sure in this case that the route does not have an overhang.
    
            If the word count of a route is low but the cosine score is high,
            we can be reasonably sure that the score is somewhat accurate. This
            is a result of a route called, for instance, 'Overhang Route'.
            Despite the low word count, it is highly likely that the route has
            an overhang on it.
    
            Finally, for routes that have both low word count and cosine score,
            we have no way to be sure of the presence (or absence) of a
            feature.  In this case, our best guess is that the route is at
            chance of featuring a given style of climbing.
    
            If we chart word count, cosine similarity, and the credibility of
            the cosine score, we are left with a cone with a point at the
            origin, reaching up at a 45 degree angle along the credibility (z)
            axis. Each route will exist somewhere on the surface of the cone.
            To make use of this, we need to calculate this position. The height
            to the cone gives us the credibility, and can be calculated with:
    
                    Credibility = sqrt(W ** 2 + C ** 2) * tan(45 degrees)
    
            Since tan(45 degrees) is 1, this simplifies to:
    
                            Credibility = sqrt(W ** 2 + C ** 2)

                               W = Word count
                               C = Cosine similarity
    
            The credibility of a route's score can be fed back into the score
            to find a weighted route score.  As the word count and cosine score
            get close to zero, the average score should play more of a role in
            the outcome. Therefore:
    
    
                Score = C * sqrt(W ** 2 + C ** 2) + (1 - C)(1 - W) * Cm
    
                                W = word count
                                C = cosine Similarity
                                Cm = Average cosine similarity across routes
    
            Finally, the scores are processed with a Sigmoid function,
            specifically the logistic function.
            
                            f(x) = L / 1 + e^(-k(x-x'))
                            
                                L = upper bound
                                e = Euler's constant
                                k = logistic growth rate
                                x' = Sigmoid midpoint
            
            By manipulating the constants in this function, we can find a
            continuous threshold-like set of values that are bounded by 0 and
            1.  The midpoint of the threshold is the mean value of the scores
            plus one standard devaition.  Therefore, the
            function used here is:

                            f(x) = 1 / (1 + e^(-100(x - x'))

                                x' = mean + sigma
                                e = Euler's constant

    
            Args:
                *styles(str): Names of the style archetypes
                table(Pandas dataframe): Master dataframe of cosine scores for
                    each route
                inplace(Boolean, default = False):
                    If inplace=False, adds new columns with weighted values.
                    If inplace=True, replaces the columns.
                    
            Returns:
                Updated SQL Database'''
    
            # Gets name for the columns to write data
            if inplace:
                count = 'word_count'
            else:
                count = 'word_count_norm'
    
            # As the word count increases, the credibility increases as a
            # logarithmic function
            table[count] = np.log(table['word_count'])
            table[count] = ((table[count] - table[count].min())
                            / (table[count].max() - table[count].min()))
    
            # Gets weighted scores for each style
            for style in styles:
                # Stores name to write data on
                if inplace:
                    column_name = style
                else:
                    column_name = style + '_weighted'
    
    
                # Find average cosine similarity across routes
                style_avg = table[style].mean()
                # Calculate weighted rating
                table[column_name] = ((table[style].values
                                       * np.sqrt(table[style].values ** 2
                                                 + table[count].values ** 2))
                                      + ((1 - table[count].values)
                                      * (1 - table[style].values)
                                      * style_avg))
                

                # Calculates final score using Sigmoid function
                table[column_name] = (
                    1 / (1 + np.e ** (-100 *
                                      (table[column_name]
                                  - (table[column_name].mean()
                                      + table[column_name].std())))))
    
            return table
    
        path += folder + 'Descriptions\\'
    
        # Run functions
        print('Getting word count.................', end=' ')
        word_count = get_word_count()
        print('Done')
        print('Getting route information..........', end=' ')
        routes = get_routes()
        print('Done')
        print('Scoring routes.....................')
        routes = score_routes(*styles,
                              word_count=word_count,
                              path=path,
                              routes=routes)
        print('Getting weighted scores............', end=' ')
        routes = weighted_scores(*styles, table=routes, inplace=True)
        routes = routes.round(4)
        print('Done')
        
        # Collects the full database
        query = 'SELECT * FROM Routes'
        all_routes = pd.read_sql(query, conn, index_col='route_id')
        
        # Combines columns in the routes dataframe with the full database if
        # they don't already exist in the full database
        updated = pd.concat([routes[~routes.index.isin(all_routes.index)],
                                    all_routes], sort=False)
        updated.update(routes)

        # Datatypes for columns
        dtype = {
            'name' : 'TEXT',
            'route_id' : 'INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE',
            'url' : 'TEXT UNIQUE',
            'stars' : 'FLOAT',
            'votes' : 'INTEGER',
            'bayes' : 'FLOAT',
            'latitude' : 'FLOAT',
            'longitude' : 'FLOAT',
            'trad' : 'BOOLEAN DEFAULT 0',
            'tr' : 'BOOLEAN DEFAULT 0',
            'sport' : 'BOOLEAN DEFAULT 0',
            'aid' : 'BOOLEAN DEFAULT 0',
            'snow' : 'BOOLEAN DEFAULT 0',
            'ice' : 'BOOLEAN DEFAULT 0',
            'mixed' : 'BOOLEAN DEFAULT 0',
            'boulder' : 'BOOLEAN DEFAULT 0',
            'alpine' : 'BOOLEAN DEFAULT 0',
            'pitches' : 'INTEGER',
            'length' : 'INTEGER',
            'nccs_rating' : 'TINYTEXT',
            'nccs_conv' : 'INTEGER',
            'hueco_rating' : 'TINYTEXT',
            'font_rating' : 'TINYTEXT',
            'boulder_conv' : 'INTERGER',
            'yds_rating' : 'TINYTEXT',
            'french_rating' : 'TINYTEXT',
            'ewbanks_rating' : 'TINYTEXT',
            'uiaa_rating' : 'TINYTEXT',
            'za_rating' : 'TINYTEXT',
            'british_rating' : 'TINYTEXT',
            'rope_conv' : 'INTEGER',
            'ice_rating' : 'TINYTEXT',
            'ice_conv' : 'INTEGER',
            'snow_rating' : 'TINYTEXT',
            'snow_conv' : 'INTEGER',
            'aid_rating' : 'TINYTEXT',
            'aid_conv' : 'INTEGER',
            'mixed_rating' : 'TINYTEXT',
            'mixed_conv' : 'INTEGER',
            'danger_rating' : 'TINYTEXT',
            'danger_conv' : 'INTEGER',
            'area_id' : 'INTEGER',
            'area_group' : 'INTEGER',
            'error' : 'INTEGER'}
        
        # Write to Database        
        updated.to_sql('Routes_TEST', con=conn, if_exists='replace', dtype = dtype)

        return

    # Gets TFIDF values for routes
    tfidf()

    # Gets cluster information for routes
    print('Filling in empty locations.........')
    print(fill_null_loc())
    
    print('Getting climbing area clusters.....', end=' ')
    cluster_text = '''SELECT route_id, latitude, longitude
                      FROM Routes'''
    clusters = pd.read_sql(cluster_text, con=conn, index_col='route_id')
    clusters = route_clusters(clusters)
    print('Done')

    print('Getting Bayesian rating............', end=' ')
    # Gets Bayesian rating for routes
    query = '''SELECT route_id, stars, votes
                    FROM Routes'''
    bayes = pd.read_sql(query, con=conn, index_col='route_id')
    bayes = bayesian_rating(bayes)
    print('Done')


    # Combines metrics
    add = pd.concat([bayes, clusters], axis=1)

    print('Writing to SQL.....................', end=' ')
    # Writes to the database
    for route in add.index:
        rate = add.loc[route]['bayes']
        group = add.loc[route]['area_group']

        cursor.execute('''UPDATE Routes
                         SET bayes = %s, area_group = %s
                         WHERE route_id = %s''', % (rate, group, route))
    conn.commit()
    print('Done')

    # Gets route scores for climbing styles
    find_route_styles('arete', 'chimney', 'crack', 'slab', 'overhang',
                      path=path)
    return 'Complete'


if __name__ == '__main__':
    print(MPAnalyzer())
