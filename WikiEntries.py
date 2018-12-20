# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 22:29:13 2018

@author: Bob
"""


from urllib.request import urlopen
from bs4 import BeautifulSoup
import sqlite3
import re
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import pandas as pd
import numpy as np



# Connect to SQLite database and create database 'Routes.sqlite'
conn = sqlite3.connect('Routes-Cleaned.sqlite')
# Create cursor
cursor = conn.cursor()


wikipage = urlopen('https://en.wikipedia.org/wiki/Slab_climbing')
# Opens HTML
html = wikipage.read()
# Parses HTML with BS package
region_soup = BeautifulSoup(html, 'html.parser')
body = region_soup.body
sections = body.find_all('p')
text = ''
for section in sections:
    text += section.get_text()
    
    
text = text.lower()
ps = PorterStemmer()
# Splits into words as a list
text = re.sub(r"[^\w\s']", '', text)

text = word_tokenize(text)
# Finds stems for each word, if there are any
text = [ps.stem(word) for word in text]
doc_length = len(text)
# Converts to dataframe
length = len(text)
text = pd.DataFrame({'word': text})['word']\
         .value_counts()\
         .rename('counts')\
         .to_frame()
         
text['tf'] = text['counts'] / length


length = np.sqrt(np.sum(text['tf'] ** 2))
text['tfidf'] = text['tf'] / length
text = text['tfidf']


query = 'SELECT word, tfidfn FROM TFIDF WHERE route_id = 50000'
idf = pd.read_sql(query, con=conn, index_col='word')['tfidfn']
print(2 * np.sum(idf * text))

ids = (45986, 31768, 36297, 13126, 7510, 38809, 6024, 106006, 29994)



