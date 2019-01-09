from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import pandas as pd
import unidecode
import sqlite3
import re
import numpy as np

conn = sqlite3.connect('C:\\Users\\Bob\Documents\\Python\Mountain Project\\Routes-Cleaned.sqlite')
cursor = conn.cursor()

# Sets display options for pandas
pd.options.display.max_rows = 1000
pd.options.display.max_columns = 10



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
    
def handler(route_id, text):
    text = text_splitter(text)
    doc_length = len(text)
    if doc_length == 0:
        text = pd.DataFrame({'route_id': route_id,
                             'word': [None],
                             'word_count': [None],
                             'tf': [None]}).set_index('route_id')
    else:
        text = pd.DataFrame({'route_id': route_id,
                             'word': text})
        text = (text.groupby('route_id').word
                .value_counts()
                .to_frame()
                .rename(columns={'word': 'word_count'}))
        text['tf'] = text['word_count'] / doc_length
    text.to_sql('Words', con=conn, if_exists='append')
    
def idf(word, num_docs):
    print('Finding IDF for', word.name)

    word['idf'] = 1 + np.log(num_docs / len(word))
    return word

def normalize(routes):
    print('Normalizing TFIDF values for', routes.name)
    length = np.sqrt(np.sum(routes['tfidf'] ** 2))
    routes['tfidfn'] = routes['tfidf'] / length
    return routes.reset_index()


def weed_out(table, min_occur, max_occur):
    if min_occur < len(table) < max_occur:
        return table.reset_index()
    
    
def tfidf(min_occur=None, max_occur=None):

    cursor.execute('SELECT COUNT(route_id) FROM Routes')
    num_docs = cursor.fetchone()[0]

    if min_occur is None:
        min_occur = 0.001 * num_docs
    if max_occur is None:
        max_occur = 0.9 * num_docs
        
    # UPDATE TO COMBINE FUNCTIONS
    query = 'SELECT route_id, word, tf FROM Words'
    routes = pd.read_sql(query, con=conn, index_col='route_id')
    routes = routes.groupby('word', group_keys=False)
    routes = routes.apply(weed_out, min_occur, max_occur)
    routes = routes.groupby('word')
    routes = routes.apply(idf, num_docs=num_docs)
    routes['tfidf'] = routes['tf'] * routes['idf']
    routes = routes.groupby('route_id', group_keys=False).apply(normalize)
    routes = routes.set_index('route_id').drop('index', axis=1)
    routes.to_sql('TFIDF', con=conn, if_exists='replace')

    return routes

routes = cursor.execute('''SELECT route_id, text from Routes
                        WHERE route_id
                        NOT IN (SELECT route_id FROM Words)''')
route = cursor.fetchone()

while route is not None:
    route_id = route[0]
    text = route[1]
    print(route_id)

    word = handler(route_id, text)
    route = cursor.fetchone()

print(tfidf())

