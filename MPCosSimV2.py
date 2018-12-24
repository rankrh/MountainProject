# -*- coding: utf-8 -*-
"""
Created on Sat Dec 22 13:46:09 2018

@author: Bob
"""

import pandas as pd
import sqlite3

conn = sqlite3.connect('Routes-Cleaned.sqlite')
cursor = conn.cursor()

path = 'Descriptions/TFIDF.csv'
pd.options.display.max_rows = 200000

query = '''SELECT route_id, url FROM Routes
           WHERE route_id IN 
           (SELECT route_id FROM Scores ORDER BY overhang DESC LIMIT 10)'''

urls = pd.read_sql(query, con=conn)

for url in urls['url']:
    print(url)
    
print(urls['route_id'])
           
           