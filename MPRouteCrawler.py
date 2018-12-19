# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 11:35:59 2018

@author: Bob

Summary:
This program crawls Mountain Project to find route data on rock climbs.

Details:
The ultimate purpose of the program is to help users optimize their time by
finding climbing areas based on their preferences.  By combining metrics such
as distance to user, type and difficulty of routes, and concentration of
routes, we can find where climbers can make best use of their time. The first
step of process is to create a database of route information. This program
grabs data from the web pages that will later be processed and organized.
Because the program depends on an internet connection, it has been written to
be restartable.  This is also useful because of the sheer number of routes on
the website require a long period of time to download.

Next-Steps:
There are roughly 180,000 routes at present, each sorted into an arbitrary
number of areas and sub-areas.  A 'next-step' would be to search the
"what's new" page:

www.mountainproject.com/
                whats-new-more-data?type=routes&locationId=0&days=0&offset=0

on a regular basis to keep on-track of new routes.  For this page, the offset
value refers to the number of routes back you want to look, and returns 36
rotues.  It therefore should always be a multiple of 36 to keep a full count.
Perhaps the best way to do this would be to pull pages in multiples of 36 until
the first route on the page has been scraped, and then get all routes before
that.
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import urllib.error
import sqlite3
import ssl
import re
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import pandas as pd
import os


def MPScraper(path='C:/Users/',
              folder='/MountainProject'):
    
    
    ''' Sets up SQL database for climbing areas and routes.
    
    Creates a database with two tables.  The first, 'Areas', holds climbing
    areas and regions.  'Regions' are defined by Mountain Project, and are
    either countries or states in the US. Climbing areas hold either other
    areas or, at the lowest level, routes. The 'Areas' table holds the columns:
        
        id - a unique identifier for the area
        name - the area name
        from_id - the id of the area that the current area falls under
            i.e., if area 12 is a sub-area of area 4, area 12 would have a
            from_id of 4
        latitude - geographic latitude for the area
        longitude - geographic latitude for the area
        error - if any errors occur while reading the URL for the area, records
            the error number
        complete - Boolean value that helps keep track of what areas have been
            visited before

    Since routes are what we really are interested in, they get their own
    table.
        name - route name
        route_id - unique identifier
        url - URL on Mountain Project
        stars - Average rating by MP users
        votes - Number of votes
        bayes - Weighted average rating
        latitude, longitude - Geographic location
        trad, tr, sport, aid, snow, ice, mixed, boulder, alpine - Boolean value
            that records the style of climbing
        pitches, length - Basic route length information
        nccs_rating, nccs_conv - alpine difficulty rating and conversion to
            decimal value
        hueco_rating, font_rating, boulder_conv - bouldering difficulty rating
            and conversion to decimal value
        yds_rating, french_rating, ewbanks_rating, uiaa_rating, za_rating, 
        british_rating, rope_conv - Roped rock climbing difficulty rating and
            conversion to decimal value
        ice_rating, ice_conv - Ice climbing difficulty rating and conversion to
            decimal value
        snow_rating, snow_conv - Snow climbing/mountaineering rating and
            conversion to decimal value
        aid_rating, aid_conv - Aid climbing difficulty rating and conversion to
            decimal value
        mixed_rating, mixed_conv - Mixed climbing difficulty rating and
            conversion to decimal value
        danger_rating, danger_conv - Route danger and conversion to decimal
            value
        area_id - Area ID for parent area
        area_group - ID of area cluster
        area_counts - Number of other routes in that route cluster
        error - ID of any errors that occur during data retrieval
        edit - Keeps track of what routes have been collected'''    
    
    
    # FIXME: Handle exceptions more elegantly and create folders, files only
    # if they need to be created
    username = os.getlogin()
    if path == 'C:/Users/':
        path += username
    try:
        os.chdir(path + folder)        
        directory = os.getcwd()
        print(directory)
    except OSError.winerror as e:
        return e
    return path



    DBname='MPRoutes'

    """
    try:
        os.chdir(path)
        try:
            os.mkdir('Test')
        except:
            try:
                os.mkdir(folder)
#            os.chdir(path + folder)
            except:
                print('Fail')
        directory = os.getcwd()
        print(directory)
        return
    except OSError:
        message = "Creation of the directory %s failed" % path
        print(message)
        return"""

    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Connect to SQLite database and create database 'Routes.sqlite'
    conn = sqlite3.connect(DBname + '.sqlite')
    # Create cursor
    cursor = conn.cursor()

    # Creates SQL DB with information on climbing areas including the latitude
    # and longitude, as well as how to access the the Mountain Project page
    # The 'complete' column tracks whether the area has been scraped before
    cursor.execute('''CREATE TABLE IF NOT EXISTS Areas(
            id INTEGER PRIMARY KEY,
            name TINYTEXT,
            url TEXT UNIQUE,
            from_id INTEGER,
            latitude FLOAT,
            longitude FLOAT,
            error INTEGER,
            complete BOOLEAN DEFAULT 0)''')

    # The lowest level pages are routes.  This DB stores all route data. The
    # 'edit' column defaults to false, and will indicate that the route has
    # been processed by the cleaner program.
    cursor.execute('''CREATE TABLE IF NOT EXISTS Routes(
            name TEXT,
            route_id INTEGER PRIMARY KEY,
            route_info TEXT,
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
            area_id INTEGER,
            area_group INTEGER,
            area_counts INTEGER
            error INTETER,
            edit BOOLEAN DEFAULT 0)''')

    def get_regions():
        """ Collects region data, the broadest category of climbing area on MP.

        'Region' refers to a state in the US, or a country outside of the US.
        Mountain Project is not well established outside of North America, so
        the number of routes in other countries is often minimal.  This
        function first finds all of the broad regions, then splits them into
        their areas. By choosing a random area that has not yet been visited
        as indicated by the 'complete' column on the areas table, the function
        can quickly determine where it has been, and is restartable. This
        requires internet connection, so any server error or issue with
        connectivity will cause the program to fail.

        Args:

        Returns:
            get_sub_areas(fn): function that expands areas
        """

        # Also known as the 'climbing directory'
        route_guide = urlopen('https://www.mountainproject.com/route-guide',
                              context=ctx)
        # Opens HTML
        region_html = route_guide.read()
        # Parses HTML with BS package
        region_soup = BeautifulSoup(region_html, 'html.parser')
        # Finds regions area of the page
        regions = region_soup.find('div', id='route-guide'
                                   ).find_all('div', class_='mb-half')

        for region in regions:
            # Link to region area guide
            url = region.find('a')['href']
            # English name of region
            region_name = region.find('a').get_text()
            # Writes region name and url to Areas DB.  This gives the region a
            # unique id automatically
            cursor.execute('''INSERT OR IGNORE INTO Areas(url, name)
                   VALUES (?, ?)''', (url, region_name))
            # Commits to DB
            conn.commit()

    def get_areas(region_id=None):
        ''' Gets sub-areas for given area or group of areas in SQL database.
        
        Mountain Project organizes climbing areas intu an arbitrary number of
        sub-areas.  This function gets the sub areas in a given area.  For each
        sub-area it finds, it finds sub-areas.  This function was written
        primarily to grab the data from region-level areas, and then pass it on
        to lower-level and route-level sub-areas.  As such, it only needs the
        area_id, while the get_sub_areas functino requires the url and name as
        well.
        
        Args:
            region_id(int): Optional locator for the region.  If no region_id
                is passed, this function will find any that has not been found
                yet.
        ReturnsL
            get_sub_areas(fn): Finds sub-areas and returns data.
        '''
        
        if region_id is None:
            # Finds one area that has not been found and pulls out the
            # information (url, name and id) that will be needed to expand it
            cursor.execute('''SELECT url, name, id FROM Areas
                                      WHERE complete IS 0
                                      AND error is Null
                                      LIMIT 1''')
            area_data = cursor.fetchone()
        else:
            cursor.execute('''SELECT url, name, id FROM Areas
                                      WHERE complete IS 0
                                      AND error ID Null AND area_id = ?
                                      LIMIT 1''', (region_id,))
            area_data = cursor.fetchone()
        # If no region is unopened, terminates function
        if area_data is None:
            return 'No more areas found.'
        url = area_data[0]
        name = area_data[1]
        area_id = area_data[2]
        # Expands areas
        return get_sub_areas(url, name, area_id)

    def get_sub_areas(main_url, main_name, from_id):

        """ Gets sub-areas given a climbing area.

        Mountain Project(MP) allows for an area to contain nested sub-areas or
        routes, but not both.  This function determines the type of area in
        question, and then parses the data accordingly.  If the area contains
        other areas, it gathers some data on location and then runs recursively
        until it finds routes.  If the climbing area only contains routes, it
        passes the area information to another function that deals with the
        routes directly.

        Args:
            main_url(str): URL of parent area
            main_name(str): English name of the parent area
            from_id(int): Area ID of the parent area

        Returns:
            If area contains other areas:
                get_sub_areas(fn): Dives deeper into nested areas and pulls
                    information
            If area contains routes:
                get_route_urls(fn): Gathers route urls for an area
        """

        # Tries to get HTML data about the area
        try:
            areas_doc = urlopen(main_url, context=ctx)

        # If HTTP error (e.g. 404 Page Not Found), logs the error in the DB and
        # moves on to the next page
        except urllib.error.HTTPError as httperror:
            error = httperror.code
            print('HTTPError: {}'.format(error))
            cursor.execute('UPDATE Areas SET error = ? WHERE url = ?',
                           (error, main_url,))
            conn.commit()
            return

        except urllib.error.URLError as error:
            print(error.reason)
            return 'Connectivity Error'

        areas_html = areas_doc.read()
        # Parses html with BS package
        areas_soup = BeautifulSoup(areas_html, 'html.parser')
        # Determines if the area is empty of route and sub-area information
        is_empty = areas_soup.find('div', class_="my-1")
        # Searches for routes in the area
        routes_in_area = areas_soup.find('td', class_="route-score")

        # If the area contains other areas, finds information on the sub-areas
        if not routes_in_area and not is_empty:
            # Updates user on progress
            print()
            print('Exploring: ', main_name)

            # Gets HTML data
            areas = areas_soup.find('div', class_='mp-sidebar')
            areas = areas.find_all('div', class_='lef-nav-row')

            # For each sub-area, scrapes information
            for area in areas:
                # Grabs current URL
                area_url = area.find('a')['href']
                # Parses HTML with BS
                sub_area_doc = urlopen(area_url, context=ctx)
                sub_area_html = sub_area_doc.read()
                sub_area_soup = BeautifulSoup(sub_area_html, 'html.parser')
                # Finds sub-area name
                area_name = sub_area_soup.body.find('h1').get_text().strip()
                # Updates user
                print('    - ', area_name, '(' + area_url + ')')
                # Finds latitude and longitude
                map_table = sub_area_soup.find('table',
                                               class_='description-details')
                map_table = map_table.get_text()
                # Uses regular expressions to find numbers that look like
                # latitude and longitude numbers
                lat_long = re.findall('[\-0-9]+\.[0-9]+', map_table)
                # Ensures that both latitude and longitude are found, and helps
                # guard against false-positives
                if len(lat_long) == 2:
                    lat = lat_long[0]
                    long = lat_long[1]
                # Otherwise gives a generic lat, long
                else:
                    lat, long = None, None

                # Updates DB with area name, URL, parent area, location
                cursor.execute('''
                               INSERT OR IGNORE INTO
                               Areas(name, url, from_id,latitude, longitude)
                               VALUES(?, ?, ?, ?, ?)''',
                               (area_name, area_url, from_id, lat, long))
                conn.commit()

        # If the area only contains routes, passes information to route
        # functions
        elif routes_in_area and not is_empty:
            # Updates user
            print()
            print('Exploring: ', main_name)

            # grabs latitude and longitude
            cursor.execute('''SELECT latitude, longitude
                              FROM Areas
                              WHERE url IS ?''', (main_url,))
            loc = cursor.fetchone()
            lat, long = loc[0], loc[1]
            get_route_urls(main_url, from_id, lat, long)
        cursor.execute('UPDATE Areas SET complete = 1 WHERE id = ?',
                       (from_id,))
        conn.commit()

    def get_route_urls(area_url, area_id, lat, long):
        """ Gets route urls given a specific area.

        The most detailed information on a route is found on its individual
        page, so the first step in grabbing the data is grabbing the URLs for
        the website.  This function iterates through the routes in an area and
        sends the URLs to the get_route_features function for final processing.

        Args:
            area_url(str): url for a specific climbing area.  MP areas can
                contain either routes or other areas, and this function only
                works on lowest-level areas.

        Returns:
            get_route_features(fn): Gathers data on the type of climbing route
        """

        # Open page html with BeautifulSoup
        area_doc = urlopen(area_url, context=ctx)
        area_html = area_doc.read()
        # Parses html with BS package
        area_soup = BeautifulSoup(area_html, 'html.parser')

        # Opens main body of page
        body = area_soup.body
        # Contains list of all routes in an area
        sidebar = body.find('div', class_='mp-sidebar')
        # Opens routes section
        class_ = 'max-height max-height-md-0 max-height-xs-150'
        table = sidebar.find('div',
                             class_=class_)
        table = table.find('table')
        routes = table.find_all('tr', id=None)
        # Gets route url and sends to get_route_features(route_url)
        for route in routes:
            route_url = route.find('a')['href']
            print('         - ', route_url)
            get_route_features(route_url, area_id, lat, long)

    def get_route_features(route_url, area_id, lat, long):
        """ Gets type of route, route difficulty, route quality, and route
        length.

        Gathers information on route name, url, stars, votes, latitude,
        longitude, type, pitches, length, rating, and terrain, as well as the
        area id of its parent area.  Creates and updates an SQL database with
        these columns.

        Args:
            route_url(str): url for climbing route
            area_id(int): Unique identifier for parent area

        Returns:
            Commits to SQL DB the following infomation:
                route_soup(str): HTML processed with BeautifulSoup
                route_url(str): URL for route
                lat(float): Route latitude
                long(float): Route longitude
                area_id(int): Unique ID for parent area
        """

        # Open page html with BeautifulSoup
        route_doc = urlopen(route_url, context=ctx)
        if route_doc.getcode() != 200:
            print("Error on page: ", route_doc.getcode())
            cursor.execute('UPDATE Routes SET error=? WHERE url=?',
                           (route_doc.getcode(), route_url))
            conn.commit()
        else:
            route_html = route_doc.read()
            # Parses html with BS package
            route_soup = BeautifulSoup(route_html, 'html.parser').prettify()

            # metadata includes name, url, lat, long, stars, and votes
            data = get_route_metadata(route_url, route_soup, lat, long)

            # Includes sport, trad, tr, etc.
            route_type = get_route_type(route_soup)
            # Includes route difficulty according to different grading systems
            route_diff = get_route_diff(route_soup)
            name = data['name']

            # Combines all dictionaries
            data.update(route_type)
            data.update(route_diff)
            data['area_id'] = area_id

            # Sends to function that updates new DB
            write_to_sql(data)

            cursor.execute('SELECT route_id FROM Routes WHERE url = ?',
                           (route_url))
            route_id = cursor.fetchone()[0]

            # Includes output from analysis of the route description and
            # comments
            get_text(route_soup, name, route_id)

    def get_route_metadata(route_url, route_soup, route_lat, route_long):
        ''' Creates dict of route name, url, location, and quality.

        Route name, location,and URL have already been found, and are held in
        the cursor, while the quality of the route can be found in the HTML.
        Mountain Project (MP) measures route quality on a four star rating
        system, with 4 being the maximum.  There is also a 'bomb' rating,
        which is rarely used - these routes are often not worth posting.
        MP uses the following guide to the five ratings:

                                Bomb = "Avoid"
                                1 Star = "OK"
                                2 Stars = "Good"
                                3 Stars = "Great"
                                4 Stars = "Classic"

        Fortunately, MP averages these ratings numerically, which is what we
        will retrieve.

        Args:
            row(tup): All route data from the raw DB
            route_soup(BS Object): HTML processed with BeautifulSoup holding
                                   all route data
        Returns:
            route_data(dict): Holds route url, name, latitude, longitude,
                              stars, and votes
        '''

        # URL, Name, and Location are in raw DB
        route_name = route_soup.body.find('h1').get_text().strip()
        # Updates user
        print('Gathering data on:', route_name)

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
        mixed, snow, ice, boulder, and alpine routes, and there is no limit to
        the number of types of different climbing styles that can apply to a
        route. Some combinations (e.g. alpine and snow, aid and mixed) are
        common, but there are uncommon combinations, too.  Often, this seems
        to be a user input error, for example, a boulder/alpine route seems
        unlikely.

        Out of convenience, because the NCCS rating is stored in the same place
        as route type on MP, this function grabs that too.  NCCS ratings refer
        to the level of commitment required, usually for alpine routes.  NCCS
        is graded out of 7 (I - VII).

        Similarly, the route length and number of pitches are gathered from
        this part of the page.  Note that while route length refers to the
        length of the climb, it seems that some users have put in route
        elevation instead. This is most often apparent when, for example,
        boulder problem is listed as being 2000 feet long.

        Args:
            route_soup(BS Object): HTML processed with BeautifulSoup holding
                                   all route data
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

        # Creates a dictionary of route types and initializes them to None,
        # also including route length, number of pitches, and NCCS rating
        climb_type = {'trad': False, 'tr': False, 'sport': False, 'aid': False,
                      'snow': False, 'ice': False, 'mixed': False,
                      'boulder': False, 'alpine': False, 'pitches': pitches,
                      'length': length, 'nccs_rating': None}

        # Matches a string starting with 'Grade', then any combination of
        # 'V', 'I' of any length, then returns the 'V', 'I' characters
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
        # and matches them to the list of all route types.  If a match is
        # found, updates the dictionary at the key of the match to a True value
        for route in all_types:
            if route in route_types:
                climb_type[route.lower()] = True

        # Returns dictionary
        return climb_type

    def get_route_diff(route_soup):
        ''' Creates dictionary of route difficulty.

        There are a number of different ways to grade routes based on the style
        of climbing and the location.  Each system is organized in a different
        way, and the system is often not logical.  This function finds the
        ratings for the route in any form they may appear, and inputs the grade
        into a dictionary of all possible rating systems.

        Args:
            route_soup(BS Object): HTML processed with BeautifulSoup holding
                                   all route data
        Returns:
            difficulty(dict): Holds route difficulty in hueco, Fontaine, YDS,
                              French, Ewbanks, UIAA, South African, British,
                              aid, mixed, snow, and ice, as well as the danger
                              rating.
        '''

        # Selects the relevant part of the HTML data
        grades = route_soup.find('h2', class_="inline-block mr-2").get_text()

        # Returns 'V' followed by any combination of digits, the word 'easy',
        # and the characters '-', and '+' if followed by whitespace and 'YDS'
        hueco = re.findall('(V[\+\-\deasy]+)\s+YDS', grades)

        # Returns any combination of digits, the letters 'A', 'B', and 'C',
        # and the characters '-' and '+' if followed by whitespace and 'Font'.
        # Returns only the letter/number rating
        font = re.findall('([\d\-\+ABC]+)\s+Font', grades)

        # Returns '5.' followed by any digits, the letters 'a' through 'd', and
        # the characters '-' and '+' OR '3rd' OR 4th OR 'Easy 5th' if followed
        # by whitespace and 'YDS'
        yds = re.findall('(5\.[\d\+\-a-d/]+|3rd|4th|Easy 5th)\s+YDS', grades)

        # Returns any digit followed by any combination of '-', '+', and the
        # letters 'a' through 'd' if it is followed by whitespace and 'French'
        french = re.findall('(\d[\-\+a-d]+)\s+French', grades)

        # Returns any two consecutive digits if they are followed by whitespace
        # and 'Ewbanks'
        ewbanks = re.findall('(\d\d)\s+Ewbanks', grades)

        # Returns any Roman Numeral using XVI and '-' and '+' if it is followed
        # by whitespace and 'UIAA'
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

        rope_conv = ['3rd', '4th', 'Easy 5th', '5.0', '5.1', '5.2', '5.3',
                     '5.4', '5.5', '5.6', '5.7', '5.7+', '5.8-', '5.8',
                     '5.8+', '5.9-', '5.9', '5.9+', '5.10a', '5.10-',
                     '5.10a/b', '5.10b', '5.10', '5.10b/c', '5.10c', '5.10+',
                     '5.10c/d', '5.10d', '5.11a', '5.11-', '5.11a/b', '5.11b',
                     '5.11', '5.11b/c', '5.11c', '5.11+', '5.11c/d', '5.11d',
                     '5.12a', '5.12-', '5.12a/b', '5.12b', '5.12', '5.12b/c',
                     '5.12c', '5.12+', '5.12c/d', '5.12d', '5.13a', '5.13-',
                     '5.13a/b', '5.13b', '5.13', '5.13b/c', '5.13c', '5.13+',
                     '5.13c/d', '5.13d', '5.14a', '5.14-', '5.14a/b', '5.14b',
                     '5.14', '5.14b/c', '5.14c', '5.14+', '5.14c/d', '5.14d',
                     '5.15a', '5.15-', '5.15a/b', '5.15b', '5.15', '5.15c',
                     '5.15+', '5.15c/d', '5.15d']

        boulder_conv = ['V-easy', 'V0-', 'V0', 'V0+', 'V0-1', 'V1-', 'V1',
                        'V1+', 'V1-2', 'V2-', 'V2', 'V2+', 'V2-3', 'V3-',
                        'V3', 'V3+', 'V3-4', 'V4-', 'V4', 'V4+', 'V4-5',
                        'V5-', 'V5', 'V5+', 'V5-6', 'V6-', 'V6', 'V6+',
                        'V6-7', 'V7-', 'V7', 'V7+', 'V7-8', 'V8-', 'V8',
                        'V8+', 'V8-9', 'V9-', 'V9', 'V9+', 'V9-10', 'V10-',
                        'V10', 'V10+', 'V10-11', 'V11-', 'V11', 'V11+',
                        'V11-12', 'V12-', 'V12', 'V12+', 'V12-13', 'V13-',
                        'V13', 'V13+', 'V13-14', 'V14-', 'V14', 'V14+',
                        'V14-15', 'V15-', 'V15', 'V15+', 'V15-16', 'V16-',
                        'V16', 'V16+', 'V16-17', 'V17-', 'V17']

        mixed_conv = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9',
                      'M10', 'M11', 'M12']

        aid_conv = ['A0', 'A1', 'A2', 'A2+', 'A3',
                    'A3+', 'A4', 'A4+', 'A5', 'A6']

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

    def get_text(route_soup, route_name, route_id):
        ''' Gathers and analyzes text data from route description and
        user comments.
        '''
        # FIXME: Add Documentation

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
        ps = PorterStemmer()
        # Splits into words as a list
        text = re.sub(r"[^\w\s']", '', text)

        text = word_tokenize(text)
        # Finds stems for each word, if there are any
        text = [ps.stem(word) for word in text]
        doc_length = len(text)
        # Converts to dataframe
        text = pd.DataFrame({'route_id': route_id, 'word': text})
        # Re-formats and counts words
        text = (text.groupby('route_id').word
                    .value_counts()
                    .to_frame()
                    .rename(columns={'word': 'word_count'}))
        text['tf'] = text['word_count'] / doc_length
        text.to_sql('Words', con=conn, if_exists='append')

    def write_to_sql(route_data):
        ''' Writes the dictionary of route data to the DB

        Takes the route data as a dictionary and creates a new row on the DB
        populated with the relevant information.  A more succinct way to do
        this would be to create a tuple from the dictionary values, but I
        chose to use a dictionary here so that if more information is later
        added to the dictionary we don't need to go back through and
        re-evaluate the index of each type of data.

        Args:
            route_data(dict): All route data:
                              name, url, stars, votes, latitude, longitude,
                              trad, tr, sport, aid, snow, ice, mixed, boulder,
                              alpine, pitches, length, nccs_rating,
                              hueco_rating, font_rating, yds_rating,
                              french_rating, ewbanks_rating, uiaa_rating,
                              za_rating, british_rating, ice_rating,
                              snow_rating, aid_rating, mixed_rating,
                              danger_rating, area_id
        Returns:
            Updated SQL Database
        '''

        # Enters data
        cursor.execute('''
                         INSERT OR IGNORE INTO
                         Routes(name, url, stars, votes, latitude, longitude,
                                trad, tr, sport, aid, snow, ice, mixed,
                                boulder, alpine, pitches, length, nccs_rating,
                                hueco_rating, font_rating, yds_rating,
                                french_rating, ewbanks_rating, uiaa_rating,
                                za_rating, british_rating, ice_rating,
                                snow_rating, aid_rating, mixed_rating,
                                danger_rating, text, area_id, boulder_conv,
                                rope_conv, ice_conv, snow_conv, aid_conv,
                                mixed_conv, danger_conv)
                         VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        ((route_data['name'],
                          route_data['url'],
                          route_data['stars'],
                          route_data['votes'],
                          route_data['latitude'],
                          route_data['longitude'],
                          route_data['trad'],
                          route_data['tr'],
                          route_data['sport'],
                          route_data['aid'],
                          route_data['snow'],
                          route_data['ice'],
                          route_data['mixed'],
                          route_data['boulder'],
                          route_data['alpine'],
                          route_data['pitches'],
                          route_data['length'],
                          route_data['nccs_rating'],
                          route_data['hueco_rating'],
                          route_data['font_rating'],
                          route_data['yds_rating'],
                          route_data['french_rating'],
                          route_data['ewbanks_rating'],
                          route_data['uiaa_rating'],
                          route_data['za_rating'],
                          route_data['british_rating'],
                          route_data['ice_rating'],
                          route_data['snow_rating'],
                          route_data['aid_rating'],
                          route_data['mixed_rating'],
                          route_data['danger_rating'],
                          route_data['text'],
                          route_data['area_id'],
                          route_data['boulder_conv'],
                          route_data['rope_conv'],
                          route_data['ice_conv'],
                          route_data['snow_conv'],
                          route_data['aid_conv'],
                          route_data['mixed_conv'],
                          route_data['danger_conv'])))

        # Commits
        conn.commit()
        # Changes edit value to 1 (True) for the route in question so that the
        # program will skip it the next time it grabs a route
        cursor.execute('''UPDATE Routes
                          SET edit = 1 WHERE url = ?''', (route_data['url'],))
        conn.commit()

    get_regions()
    
    error = None
    while error == None:
        error = get_areas(region_id=None)
        

if __name__ == '__main__':
    print(MPScraper())
# FIXME: See what else needs to be included for a __main__ file


