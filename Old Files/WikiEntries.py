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
import unidecode



# Connect to SQLite database and create database 'Routes.sqlite'
conn = sqlite3.connect('Routes-Cleaned.sqlite')
# Create cursor
cursor = conn.cursor()
path = 'C:/Users/Bob/Documents/Python/Mountain Project/Descriptions/'



def tf(text, name):
    text = text.lower()
    ps = PorterStemmer()
    # Splits into words as a list
    text = re.sub(r"[^\w\s']", '', text)
    text = unidecode.unidecode(text)
    text = word_tokenize(text)
    # Finds stems for each word, if there are any
    text = [ps.stem(word) for word in text]
    # Converts to dataframe
    length = len(text)
    text = pd.DataFrame({'word': text})['word']\
             .value_counts()\
             .rename('counts')\
             .to_frame()
             
    text['tf'] = text['counts'] / length
    text.to_csv(path + name)
    
    
    
def wiki_tf(url, name):
    page = urlopen(url)
    # Opens HTML
    html = page.read()
    # Parses HTML with BS package
    region_soup = BeautifulSoup(html, 'html.parser')
    body = region_soup.body
    sections = body.find_all('p')
    text = ''
    for section in sections:
        text += section.get_text()
    return text
    tf(text, name)
        
def thought_co(url):
    page = urlopen(url)
    # Opens HTML
    html = page.read()
    # Parses HTML with BS package
    soup = BeautifulSoup(html, 'html.parser')
    article = soup.find_all('div',
                            class_='comp mntl-sc-block mntl-sc-block-html')
    headings = soup.find_all('h3',
                             class_='comp mntl-sc-block mntl-sc-block-heading')
    
    text = ''
    for section in article:
        text += section.get_text()
    for heading in headings:
        text += heading.get_text()
    tf(text, name)
    
wikipages = {'crack': 'https://en.wikipedia.org/wiki/Crack_climbing',
             'overhang': 'https://en.wikipedia.org/wiki/Overhang_(rock_formation)',
             'slab': 'https://en.wikipedia.org/wiki/Slab_climbing',
             'face': 'https://en.wikipedia.org/wiki/Face_climbing',}

thoughtcopages = {'chimney': 'https://www.thoughtco.com/how-to-climb-chimneys-755279',
                 'arete': 'https://www.thoughtco.com/how-to-climb-aretes-755292'}

  
for name, url in wikipages.items():
    file = open(path + name + '.txt', 'w', encoding='utf-8')
    file.write(wiki_tf(url, name))

for name, url in thoughtcopages.items():
    file = open(path + name + '.txt', 'w', encoding='utf-8')
    file.write(thought_co(url))


        
        

    

