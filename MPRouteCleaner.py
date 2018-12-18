# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 18:15:57 2018

@author: Bob

Summary:
    Cleans and organizes route data

Details:
    Gathers information on route name, url, stars, votes, latitude, longitude,
    type, pitches, length, rating, and terrain, as well as the area id of
    its parent area.  Creates and updates an SQL database with these columns.

Next-Steps:
    Implement machine learning to help make the terrain functions work better
"""
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import sqlite3
import re

# Connects to DB with raw route data and creates a cursor
full_conn = sqlite3.connect('Routes-Raw.sqlite')
full_cur = full_conn.cursor()

# Connects to DB that will store processed route data and creates a cursor
edit_conn = sqlite3.connect('Routes-Cleaned.sqlite')
edit_cur = edit_conn.cursor()

# Creates a table on the new DB for the processed routes
edit_cur.execute('''
                 CREATE TABLE IF NOT EXISTS Routes(
                    name TEXT,
                    route_id INTEGER PRIMARY KEY,
                    url TEXT UNIQUE,
                    stars FLOAT,
                    votes INTEGER,
                    bayes FLOAT,
                    latitude FLOAT,
                    longitude FLOAT,
                    trad BOOLEAN DEFAULT 0,
                    tr BOOLEAN DEFAULT 0,
                    sport BOOLEAN DEFAULT 0,
                    aid BOOLEAN DEFAULT 0,
                    snow BOOLEAN DEFAULT 0,
                    ice BOOLEAN DEFAULT 0,
                    mixed BOOLEAN DEFAULT 0,
                    boulder BOOLEAN DEFAULT 0,
                    alpine BOOLEAN DEFAULT 0,
                    pitches INTEGER,
                    length INTEGER,
                    nccs_rating TINYTEXT,
                    nccs_conv INTEGER,
                    hueco_rating TINYTEXT,
                    font_rating TINYTEXT,
                    boulder_conv INTERGER,
                    yds_rating TINYTEXT,
                    french_rating TINYTEXT,
                    ewbanks_rating TINYTEXT,
                    uiaa_rating TINYTEXT,
                    za_rating TINYTEXT,
                    british_rating TINYTEXT,
                    rope_conv INTEGER,
                    ice_rating TINYTEXT,
                    ice_conv INTEGER,
                    snow_rating TINYTEXT,
                    snow_conv INTEGER,
                    aid_rating TINYTEXT,
                    aid_conv INTEGER,
                    mixed_rating TINYTEXT,
                    mixed_conv INTEGER,
                    danger_rating TINYTEXT,
                    danger_conv INTEGER,
                    text TEXT,
                    tfidf BOOLEAN,
                    area_id INTEGER,
                    area_group INTEGER,
                    area_counts INTEGER)''')


def get_route():
    ''' Selects a route to explore from the raw DB, then passes to processing
    functions.

    This function begins by choosing a route from the Routes tale of the raw
    DB based on the column 'edit'.  This column holds a boolean value that is
    True if the route has already been processed and False if not.  Note that
    SQL uses 1 and 0 to denote True, False respectively, and that the edit
    column is initialized to 0.  When the route is fully processed, the 'edit'
    value will be passed as 'True'.

    Args:
    Returns:
        write_to_sql(fn): Function that commits information to the SQL DB that
                          hosts processed route data.
    '''

    # Select a route from the raw DB that has not been processed
    full_cur.execute('''
                     SELECT * FROM Routes
                     WHERE edit IS not 1
                     LIMIT 1''')
    row = full_cur.fetchone()
    # Loop until there are no un-processed routes

    while row is not None:

        # Column 1 is HTML data
        route_html = row[0]
        # Column 5 is the unique area_id value of the route's area
        area_id = row[4]
        # Parses html with BS package
        route_soup = BeautifulSoup(route_html, 'html.parser')

        # metadata includes name, url, lat, long, stars, and votes
        data = get_route_metadata(row, route_soup)
        # Includes sport, trad, tr, etc.
        route_type = get_route_type(route_soup)
        # Includes route difficulty according to different grading systems
        route_diff = get_route_diff(route_soup)
        name = data['name']
        # Includes output form analysis of the route description and comments
        text = get_text(route_soup, name)

        # Combines all dictionaries
        data.update(route_type)
        data.update(route_diff)
        data['area_id'] = area_id
        data['text'] = text

        # Sends to function that updates new DB
        write_to_sql(data)
        
        full_cur.execute('''
                     SELECT * FROM Routes
                     WHERE edit IS not 1
                     LIMIT 1''')
        row = full_cur.fetchone()
    fill_null_loc()
    
    cluster_text = '''SELECT route_id, latitude, longitude
                      FROM Routes'''
    clusters = pd.read_sql(cluster_text, con=edit_conn, index_col='route_id')
    clusters = route_clusters(clusters)
    
    bayes_text = '''SELECT route_id, stars, votes
                    FROM Routes'''
    bayes = pd.read_sql(bayes_text, con=edit_conn, index_col='route_id')
    bayes = bayesian_rating(bayes)['bayes']
    
    add = pd.concat([bayes, clusters], axis=1)
    
    for route in add.index:
        rate = add.loc[route]['bayes']
        group = add.loc[route]['area_group']
        cnt = add.loc[route]['area_counts']
    
        edit_cur.execute('''UPDATE Routes
                         SET bayes = ?, area_group = ?, area_counts = ?
                         WHERE route_id = ?''', (rate, group, cnt, route))
        edit_conn.commit()


def get_route_metadata(row, route_soup):
    ''' Creates dict of route name, url, location, and quality.

    Route name, location,and URL have already been found, and are held in
    the cursor, while the quality of the route can be found in the HTML.
    Mountain Project (MP) measures route quality on a four star rating system,
    with 4 being the maximum.  There is also a 'bomb' rating, which is rarely
    used - these routes are often not worth posting.  MP uses the following
    guide to the five ratings:

                            Bomb = "Avoid"
                            1 Star = "OK"
                            2 Stars = "Good"
                            3 Stars = "Great"
                            4 Stars = "Classic"

    Fortunately, MP averages these ratings numerically, which is what we will
    retrieve.

    Args:
        row(tup): All route data from the raw DB
        route_soup(BS Object): HTML processed with BeautifulSoup holding all
                               route data
    Returns:
        route_data(dict): Holds route url, name, latitude, longitude, stars,
                          and votes
    '''

    # URL, Name, and Location are in raw DB
    route_url = row[1]
    route_name = route_soup.body.find('h1').get_text().strip()
    # Updates user
    print('Gathering data on:', route_name)
    route_lat, route_long = row[2], row[3]

    # Average number of stars awarded out of 4
    stars = route_soup.find('a', class_='show-tooltip', title='View Stats')
    stars = stars.get_text().strip().split()[1]

    # Number of votes cast
    votes = route_soup.find('a', class_='show-tooltip', title='View Stats')
    votes = votes.get_text().strip().split()[3]
    votes = re.sub(',', '', votes)

    # Creates a dictionary and sends to the main function
    route_data = {'name': route_name, 'url': route_url, 'stars': stars,
                  'votes': votes, 'latitude': route_lat,
                  'longitude': route_long}
    
    return route_data


def get_route_type(route_soup):
    ''' Creates dictionary of route type (e.g. sport, trad, boulder, etc)

    This function gathers data on what types of climbing can be done on a
    specific route. Mountain Project (MP) hosts trad, top rope, sport, aid,
    mixed, snow, ice, boulder, and alpine routes, and there is no limit to the
    number of types of different climbing styles that can apply to a route.
    Some combinations (e.g. alpine and snow, aid and mixed) are common, but
    there are uncommon combinations, too.  Often, this seems to be a user
    input error, for example, a boulder/alpine route seems unlikely.

    Out of convenience, because the NCCS rating is stored in the same place as
    route type on MP, this function grabs that too.  NCCS ratings refer to the
    level of commitment required, usually for alpine routes.  NCCS is graded
    out of 7 (I - VII).

    Similarly, the route length and number of pitches are gathered from this
    part of the page.  Note that while route length refers to the length of
    the climb, it seems that some users have put in route elevation instead.
    This is most often apparent when, for example, a boulder problem is listed
    as being 2000 feet long.

    Args:
        route_soup(BS Object): HTML processed with BeautifulSoup holding all
                               route data
    Returns:
        climb_type(dict): Holds boolean value for each route type 'Trad',
                          'TR', 'Sport', 'Aid', 'Snow', 'Ice', 'Mixed',
                          'Boulder', 'Alpine'
    '''

    # Grab relevent web data
    route_info = route_soup.find('table', class_='description-details')
    route_info = route_info.find_all('td')[1].get_text().strip()

    # Matches a string of digits of any length followed by 'ft'
    length = re.findall('([\d]+) ft', route_info)
    # Returns a list
    if length:
        length = length[0]
    # If the list is empty, returns None
    else:
        length = None

    # Matches a string of digits of any length followed by 'pitches'
    pitches = re.findall('([\d]+) pitches', route_info)
    # Returns a list
    if pitches:
        pitches = pitches[0]
    # If the list is empty, returns None
    else:
        pitches = None
        
    # Creates a dictionary of route types and initializes them to None, also
    # including route length, number of pitches, and NCCS rating
    climb_type = {'trad': False, 'tr': False, 'sport': False, 'aid': False,
                  'snow': False, 'ice': False, 'mixed': False,
                  'boulder': False, 'alpine': False, 'pitches': pitches,
                  'length': length, 'nccs_rating': None}


    # Matches a string starting with 'Grade', then any combination of 'V', 'I'
    # of any length, then returns the 'V', 'I' characters
    nccs = re.findall('Grade ([VI]+)', route_info)
    nccs_conv = ['I', 'II', 'III', 'IV', 'V', 'VI']
    # Returns a list
    if nccs:
        nccs = nccs[0]
        try:
            climb_type['nccs_conv'] = nccs_conv.index(nccs)
        except:
            climb_type['nccs_conv'] = -1
    # If the list is empty, returns None
    else:
        nccs = None

    # All allowed MP route types
    all_types = ['Trad', 'TR', 'Sport', 'Aid', 'Snow', 'Ice', 'Mixed',
                 'Boulder', 'Alpine']
    # Creates a list of types for the route in question
    route_types = route_info.split(', ')


    # Searches through the list of route types for the route in question
    # and matches them to the list of all route types.  If a match is found,
    # updates the dictionary at the key of the match to a True value
    for route in all_types:
        if route in route_types:
            climb_type[route.lower()] = True

    # Returns dictionary
    return climb_type


def get_route_diff(route_soup):
    ''' Creates dictionary of route difficulty.

    There are a number of different ways to grade routes based on the style of
    climbing and the location.  Each system is organized in a different way,
    and the system is often not logical.  This function finds the ratings for
    the route in any form they may appear, and inputs the grade into a
    dictionary of all possible rating systems.

    Args:
        route_soup(BS Object): HTML processed with BeautifulSoup holding all
                               route data
    Returns:
        difficulty(dict): Holds route difficulty in hueco, Fontaine, YDS,
                          French, Ewbanks, UIAA, South African, British, aid,
                          mixed, snow, and ice, as well as the danger rating.
    '''

    # Selects the relevant part of the HTML data
    grades = route_soup.find('h2', class_="inline-block mr-2").get_text()

    # Returns 'V' followed by any combination of digits, the word 'easy',
    # and the characters '-', and '+' if followed by whitespace and 'YDS'
    hueco = re.findall('(V[\+\-\deasy]+)\s+YDS', grades)

    # Returns any combination of digits, the letters 'A', 'B', and 'C', and
    # the characters '-' and '+' if followed by whitespace and 'Font'.
    # Returns only the letter/number rating
    font = re.findall('([\d\-\+ABC]+)\s+Font', grades)

    # Returns '5.' followed by any digits, the letters 'a' through 'd', and
    # the characters '-' and '+' OR '3rd' OR 4th OR 'Easy 5th' if followed by
    # whitespace and 'YDS'
    yds = re.findall('(5\.[\d\+\-a-d/]+|3rd|4th|Easy 5th)\s+YDS', grades)

    # Returns any digit followed by any combination of '-', '+', and the
    # letters 'a' through 'd' if it is followed by whitespace and 'French'
    french = re.findall('(\d[\-\+a-d]+)\s+French', grades)

    # Returns any two consecutive digits if they are followed by whitespace
    # and 'Ewbanks'
    ewbanks = re.findall('(\d\d)\s+Ewbanks', grades)

    # Returns any Roman Numeral using XVI and '-' and '+' if it is followed by
    # whitespace and 'UIAA'
    uiaa = re.findall('([XVI\+\-]+)\s+UIAA', grades)

    # Returns any number if it is followed by whitespace and 'ZA'
    za = re.findall('(\d+)\s+ZA', grades)

    # Returns any combination of the letters 'MDVSHE' and any digit then a
    # space, then any digit and the letters 'abc', if they are followed by
    # whitespace and 'British'
    brit = re.findall('([MDVSHE\d]+ [\dabc]+)\s+British', grades)

    # Returns 'A' OR 'C' and any number or '-'
    aid_rate = re.findall('(A[\d\+]+|C[\d\+]+)', grades)

    # Returns 'M' followed by any number
    mixed_rate = re.findall('(M[0-4]+)', grades)

    # Returns X OR R OR PG13
    danger = re.findall('(X|R|PG13)', grades)

    # Returns any word if it is followed by 'Snow'
    snow_rate = re.findall('([A-Za-z]+)\s+Snow', grades)

    # Returns 'WI' followed by any number
    ice_rate = re.findall('(WI\d\+)', grades)

    # Holds route difficulty information
    difficulty = {'hueco_rating': hueco, 'font_rating': font,
                  'yds_rating': yds, 'french_rating': french,
                  'ewbanks_rating': ewbanks, 'uiaa_rating': uiaa,
                  'za_rating': za, 'british_rating': brit,
                  'ice_rating': ice_rate, 'snow_rating': snow_rate,
                  'aid_rating': aid_rate, 'mixed_rating': mixed_rate,
                  'danger_rating': danger}
    
    rope_conv = ['3rd', '4th', 'Easy 5th', '5.0', '5.1', '5.2', '5.3', '5.4',
                 '5.5', '5.6', '5.7', '5.7+', '5.8-', '5.8', '5.8+', '5.9-',
                 '5.9', '5.9+', '5.10a', '5.10-', '5.10a/b', '5.10b', '5.10',
                 '5.10b/c', '5.10c', '5.10+', '5.10c/d', '5.10d', '5.11a',
                 '5.11-', '5.11a/b', '5.11b', '5.11', '5.11b/c', '5.11c',
                 '5.11+', '5.11c/d', '5.11d', '5.12a', '5.12-', '5.12a/b',
                 '5.12b', '5.12', '5.12b/c', '5.12c', '5.12+', '5.12c/d',
                 '5.12d', '5.13a', '5.13-', '5.13a/b', '5.13b', '5.13',
                 '5.13b/c', '5.13c', '5.13+', '5.13c/d', '5.13d', '5.14a',
                 '5.14-', '5.14a/b', '5.14b', '5.14', '5.14b/c', '5.14c',
                 '5.14+', '5.14c/d', '5.14d', '5.15a', '5.15-', '5.15a/b',
                 '5.15b', '5.15', '5.15c', '5.15+', '5.15c/d', '5.15d']
    
    boulder_conv  = ['V-easy', 'V0-', 'V0', 'V0+', 'V0-1', 'V1-', 'V1', 'V1+',
                     'V1-2', 'V2-', 'V2', 'V2+', 'V2-3', 'V3-', 'V3', 'V3+',
                     'V3-4', 'V4-', 'V4', 'V4+', 'V4-5', 'V5-', 'V5', 'V5+',
                     'V5-6', 'V6-', 'V6', 'V6+', 'V6-7', 'V7-', 'V7', 'V7+',
                     'V7-8', 'V8-', 'V8', 'V8+', 'V8-9', 'V9-', 'V9', 'V9+',
                     'V9-10', 'V10-', 'V10', 'V10+', 'V10-11', 'V11-', 'V11',
                     'V11+', 'V11-12', 'V12-', 'V12', 'V12+', 'V12-13', 'V13-',
                     'V13', 'V13+', 'V13-14', 'V14-', 'V14', 'V14+', 'V14-15',
                     'V15-', 'V15', 'V15+', 'V15-16', 'V16-', 'V16', 'V16+',
                     'V16-17', 'V17-', 'V17']
    
    mixed_conv = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10',
                  'M11', 'M12']
    
    aid_conv = ['A0', 'A1', 'A2', 'A2+', 'A3', 'A3+', 'A4', 'A4+', 'A5', 'A6']
    ice_conv = ['WI1', 'WI2', 'WI3', 'WI4', 'WI5', 'WI6', 'WI7', 'WI8']
    danger_conv = ['PG13', 'R', 'X']
    snow_conv = ['Easy', 'Mod', 'Steep']

    conversion = {'boulder_conv': None, 'rope_conv': None,
              'ice_conv': None, 'snow_conv': None, 'aid_conv': None,
              'mixed_conv': None, 'danger_conv': None}


    # Converts [] to None and ['x'] to 'x'
    for item in difficulty:
        if not difficulty[item]:
            difficulty[item] = None
        else:
            difficulty[item] = difficulty[item][0]        
            if item is 'yds_rating':
                try:
                    rope = rope_conv.index(difficulty[item])
                    conversion['rope_conv'] = rope
                except:
                    conversion['rope_conv'] = -1
            elif item is 'hueco_rating':
                try:
                    boulder = boulder_conv.index(difficulty[item])
                    conversion['boulder_conv'] = boulder
                except:
                    conversion['boulder_conv'] = -1
            elif item is 'ice_rating':
                try:
                    ice = ice_conv.index(difficulty[item])
                    conversion['ice_conv'] = ice
                except:
                    conversion['ice_conv'] = -1
            elif item is 'snow_rating':
                try:
                    snow = snow_conv.index(difficulty[item])
                    conversion['snow_conv'] = snow
                except:
                    conversion['snow_conv'] = -1
            elif item is 'aid_rating':
                try:
                    aid = aid_conv.index(difficulty[item])
                    conversion['aid_conv'] = aid
                except:
                    conversion['aid_conv'] = -1
            elif item is 'mixed_rating':
                try:
                    mixed = mixed_conv.index(difficulty[item])
                    conversion['mixed_conv'] = mixed
                except:
                    conversion['mixed_conv'] = -1
            elif item is 'danger_rating':
                try:    
                    danger = danger_conv.index(difficulty[item])
                    conversion['danger_conv'] = danger
                except:
                    conversion['danger_conv'] = -1
    difficulty.update(conversion)

    return difficulty


def get_text(route_soup, route_name):
    ''' Gathers and analyzes text data from route description and
    user comments.
    '''

    # Finds comment section of the BS data
    cmt = 'comment-body max-height max-height-md-300 max-height-xs-150'
    comments = route_soup.find_all('div', class_=cmt)
    # Finds description of the route of BS data
    description = route_soup.find('div', class_="fr-view").get_text()

    # Creates a single text that combines the description, route name and
    # user comments that can be searched for keywords
    text = route_name + description
    for comment in comments:
        comment = comment.get_text().strip().split('\n')[0].strip()
        text += ' ' + comment
    # Want to match both upper and lowercase instances
    text = text.lower()
    

    return text


def write_to_sql(route_data):
    ''' Writes the dictionary of route data to the DB

    Takes the route data as a dictionary and creates a new row on the DB
    populated with the relevant information.  A more succinct way to do this
    would be to create a tuple from the dictionary values, but I chose to use
    a dictionary here so that if more information is later added to the
    dictionary we don't need to go back through and re-evaluate the index of
    each type of data.

    Args:
        route_data(dict): All route data - name, url, stars, votes, latitude,
                          longitude, trad, tr, sport, aid, snow, ice, mixed,
                          boulder, alpine, pitches, length, nccs_rating,
                          hueco_rating, font_rating, yds_rating, french_rating,
                          ewbanks_rating, uiaa_rating, za_rating,
                          british_rating, ice_rating, snow_rating, aid_rating,
                          mixed_rating, danger_rating, slab, overhang,
                          vertical, face, crack, chimney, area_id
    Returns:
        Updated SQL Database
    '''

    # Enters data    
    edit_cur.execute('''
                     INSERT OR IGNORE INTO
                     Routes(name, url, stars, votes, latitude, longitude, trad,
                            tr, sport, aid, snow, ice, mixed, boulder, alpine,
                            pitches, length, nccs_rating, hueco_rating,
                            font_rating, yds_rating, french_rating,
                            ewbanks_rating, uiaa_rating, za_rating,
                            british_rating, ice_rating, snow_rating,
                            aid_rating, mixed_rating, danger_rating, text,
                            area_id, boulder_conv, rope_conv, ice_conv,
                            snow_conv, aid_conv, mixed_conv, danger_conv)
                     VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?, ?)''',
                     ((route_data['name'], route_data['url'],
                       route_data['stars'], route_data['votes'],
                       route_data['latitude'], route_data['longitude'],
                       route_data['trad'], route_data['tr'],
                       route_data['sport'], route_data['aid'],
                       route_data['snow'], route_data['ice'],
                       route_data['mixed'], route_data['boulder'],
                       route_data['alpine'], route_data['pitches'],
                       route_data['length'], route_data['nccs_rating'],
                       route_data['hueco_rating'], route_data['font_rating'],
                       route_data['yds_rating'], route_data['french_rating'],
                       route_data['ewbanks_rating'], route_data['uiaa_rating'],
                       route_data['za_rating'], route_data['british_rating'],
                       route_data['ice_rating'], route_data['snow_rating'],
                       route_data['aid_rating'], route_data['mixed_rating'],
                       route_data['danger_rating'], route_data['text'],
                       route_data['area_id'], route_data['boulder_conv'],
                       route_data['rope_conv'], route_data['ice_conv'],
                       route_data['snow_conv'], route_data['aid_conv'],
                       route_data['mixed_conv'], route_data['danger_conv'])))
                     
                     
    # Commits
    edit_conn.commit()
    # Changes edit value to 1 (True) for the route in question so that the
    # program will skip it the next time it grabs a route
    full_conn.execute('''
                      UPDATE Routes
                      SET edit = 1 WHERE url = ?''', (route_data['url'],))
    full_conn.commit()
    

def fill_null_loc():
    edit_cur.execute('''SELECT route_id, area_id, name FROM Routes
                      WHERE latitude is Null or longitude is Null LIMIT 1''')
    route = edit_cur.fetchone()
    
    while route is not None:
        rid = route[0]
        fid = route[1]
        name = route[2]
        print('Processing:', name)

        lat, long = None, None
        while lat == None or long == None:
            full_cur.execute('''
                            SELECT latitude, longitude, from_id
                            FROM Areas
                            WHERE id = ?''', (fid,))
            loc = full_cur.fetchone()
            lat, long = loc[0], loc[1]
            fid = loc[2]
            
        edit_cur.execute('''UPDATE Routes
                          SET latitude = ?, longitude = ?
                          WHERE route_id = ?''', (lat, long, rid))
        edit_conn.commit()
        edit_cur.execute('''SELECT route_id, area_id, name FROM Routes
                          WHERE latitude is Null 
                          OR longitude is Null LIMIT 1''')
        route = edit_cur.fetchone()
    return 'Done'    


def bayesian_rating(routes):
    ''' Updates route quality with weighted average.
    
    The Bayesian average rating system helps to mitigate the effects of user
    ratings for routes that only have a few reviews.  The weighted rating
    works by first finding the average rating for all routes, and using that
    to bring low-rated routes up and high-rated routes down.  Essentially, the
    function gives each route phantom-users who all give the route the
    average score.  For routes with a high number of ratings the effect of the
    additional phantom users is minimal, but for routes with only one or two
    actual user ratings, the effect is large.  This keeps 4-star rated routes
    from dominating the sorting algorithm if they only have a few votes, and
    helps promote unrated routes that may be quality.
    
    Args:
        routes(pandas df): Pulled from cleaned route SQL DB with columns:
                            - route_id (int, unique)
                                Unique route identifies
                            - stars (float)
                                Raw average rating
                            - votes (int)
                                Number of user ratings
    Returns:
        routes(pandas df): Updated dataframe with Bayes rating and columns:
                            - route_id (int, unique)
                                Unique route identifies
                            - bayes (float)
                                Weighted average rating
    '''
    # Average rating of all routes
    stars = pd.read_sql('SELECT stars FROM Routes', con=edit_conn)
    avg_stars = np.mean(stars)['stars']

    # Weighted Bayesian rating
    routes['bayes'] = (((routes['votes'] * routes['stars']) + (10 * avg_stars))
                        / (routes['votes'] + 10))        
    return routes


def route_clusters(routes):
    ''' Clusters routes into area groups that are close enough to travel
    between when finding climbing areas.

    Routes can be sorted into any number of sub-areas below the 'region'
    parent.  By clustering the routes based on latitude and longitude instead
    of the name of the areas and parent areas, the sorting algorithm will be
    able to more accurately determine which routes are close together.  This
    function uses SciKit's Density Based Scan clustering algorithm.  The
    algorithm works by grouping points together in space based on upper-limits
    of distance and minimum numbers of members of a cluster.  More generally,
    the algorithm first finds the epsilon neighborhood of a point. This is the
    set of all points whose distance from a given point is less than a
    specified value epsilon.  Then, it finds the connected core-points, which
    are the points that have at least the minimum number of connected points
    in its neighborhood. Non-core points are ignored here.  Finally, the
    algorithm assigns each non-core point to a nearby cluster if is within
    epsilon, or assigns it to noise if it is not.

    The advantages of this is that the scan clusters data of any shape, has a
    robust response to outliers and noise, and that the epsilon and min points
    variables can be adjusted.

    This function returns the label/name for the cluster that a route appears
    in, as well as the number of other routes in that same cluster.  This will
    allow the sorting algorithm to more heavily weight routes that are
    clustered near others.    


    Args:
        routes(pandas df): Pulled from cleaned route SQL DB with columns:
                            - route_id (int, unique)
                                Unique route identifies
                            - latitude (float)
                            - longitude (float)
    Returns:
        routes(pandas df): Updated with clustered area group number
                            - route_id (int, unique)
                                Unique route identifies
                            - area_group (int)
                                Cluster id
                            - area_counts (int)
                                Number of routes in cluster
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
    epsilon = 0.007
    # Min number of routes in a cluster
    min_routes = 3
    # Distance baced scan
    db = DBSCAN(eps=epsilon, min_samples=min_routes).fit(locs)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    # Cluster names
    labels = db.labels_
    unique, counts = np.unique(labels, return_counts=True)
    counts = dict(zip(unique, counts))
    # Number of routes in the same cluster as a given route
    area_counts = []
    # Find area clusters
    for label in labels:
        if label >=0:
            # Counts number of routes
            area_counts.append(counts[label])
        # Areas are given a cluster id of -1 if the are not part of a cluster
        elif label == -1:
            # If so, there is only 1 route in their 'cluster'
            area_counts.append(1)
            
    routes['area_group'] = labels
    routes['area_counts'] = area_counts
    routes = routes[['area_group', 'area_counts']]
    return routes


# Starts program
get_route()


