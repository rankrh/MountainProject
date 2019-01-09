from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import pandas as pd
import numpy as np
import sqlite3
import os
import re
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import unidecode
from nltk.corpus import stopwords


path = os.getcwd()

# Connect to SQLite database and create database 'Routes.sqlite'
conn = sqlite3.connect('Routes-Cleaned.sqlite')
# Create cursor
cursor = conn.cursor()

pd.options.display.max_rows = 999


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
    return table

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
        print(route.name)

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
        archetypes = normalize(*styles, table=archetypes, inplace=True)
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

        This final score is then normalized, and represents the percent
        chance that a given route has a given feature.

        Args:
            *styles(str): Names of the style archetypes
            table(Pandas dataframe): Master dataframe of cosine scores for
                each route
            inplace(Boolean, default = False):
                If inplace=False, adds new columns with weighted values.
                If inplace=True, replaces the columns.'''

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

            # Normalizes cosine score
            max_val = table[style].max()
            table[column_name] = table[style] / max_val

            # Find average cosine similarity across routes
            style_avg = table[style].mean()
            # Calculate weighted rating
            table[column_name] = ((table[style].values
                                   * np.sqrt(table[style].values ** 2
                                             + table[count].values ** 2))
                                  + ((1 - table[count].values)
                                  * (1 - table[style].values)
                                  * style_avg))

            # Normalize weighted average
            table[column_name] = table[style] / table[style].max()
        # Select route style columns from database
        #table = table[list(styles)]

        return table

    path += '\\Descriptions\\'

    # Run functions
    print('Getting unique words')
    word_count = get_word_count()
    print('Getting route data')
    routes = get_routes()
    print('Scoring routes')
    routes = score_routes(*styles,
                          word_count=word_count,
                          path=path,
                          routes=routes)
    print(routes)
    print('Getting weighted scores')
    routes = weighted_scores(*styles, table=routes, inplace=True)

    # Write to Database
    routes.to_sql('Terrain', con=conn, if_exists='replace')
    return


find_route_styles('arete', 'chimney', 'crack', 'slab', 'overhang', path=path)
