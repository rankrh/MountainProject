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

query = 'SELECT * FROM Routes'

data = pd.read_sql(query, con=conn)
print(len(data))
data = data.drop_duplicates(subset='route_id')
#data.to_sql('Words', con=conn, if_exists='replace')
print(len(data))
