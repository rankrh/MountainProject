from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import urllib.error
import unidecode
import sqlite3
import ssl
import re
import os

conn = sqlite3.connect('Routes-Cleaned.sqlite')
# Create cursor
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
