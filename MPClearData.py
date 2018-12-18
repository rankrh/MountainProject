# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 18:15:57 2018

@author: Bob

Deletes and restarts Database information
"""

import sqlite3

full_conn = sqlite3.connect('Routes-Raw.sqlite')
full_cur = full_conn.cursor()

edit_conn = sqlite3.connect('Routes-Cleaned.sqlite')
edit_cur = edit_conn.cursor()

def clear_all_routes():
    print('''Are you sure you want to delete the entire database, including
          all data on all routes and areas?  This is irreversible.
          To continue, type: "Delete"\n''')
    if input() == 'Delete':
        print('Deleting all records')
        full_conn.execute('DROP TABLE IF EXISTS Routes')
        full_conn.execute('DROP TABLE IF EXISTS Areas')
    else:
        print('Aborted')
    
def clear_edited_routes():  
    print('''Are you sure you want to delete the processed data?\nTo continue, type: "Delete"\n''')
    if input() == 'Delete':
        full_conn.execute('UPDATE Routes SET edit = 0 WHERE edit = 1')
        full_conn.commit()
        edit_conn.execute('DROP TABLE IF EXISTS Routes')
    else:
        print('Aborted')

    
clear_edited_routes()