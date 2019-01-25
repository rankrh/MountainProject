# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 11:52:00 2019

@author: Bob
"""

import os
import sqlite3
import pandas as pd

username = os.getlogin()
path = 'C:\\Users\\'
path += username + '\\'
folder = 'Mountain Project\\'
os.chdir(path + folder)
DBname = 'MPRoutes'


# Connect to SQLite database and create database 'Routes.sqlite'
conn = sqlite3.connect(DBname + '.sqlite')
# Create cursor
cursor = conn.cursor()

query = 'SELECT * FROM Words'

data = pd.read_sql(query, con=conn)

def drop_dupes(table):
    table = table.drop_duplicates(subset='word')
    return table[['route_id', 'word', 'word_count', 'tf']]

data = data.groupby('route_id').apply(drop_dupes).set_index(['route_id', 'word'])
data.to_sql('Words', con=conn, if_exists='replace')