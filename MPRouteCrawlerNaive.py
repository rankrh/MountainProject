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
routes, we can find where climbers can best use their time. The first step of
the process is to create a database of route information. This program grabs
raw data from the web pages that will later be processed and organized.
Because the program depends on an internet connection, it has been written to
be restartable.  This is also useful because of the sheer number of routes on
the website require a long period of time to download.

Next-Steps:
There are roughly 180,000 routes at present, each sorted into an arbitrary
number of areas and sub-areas.  A 'next-step' would be to search the
"what's new" page (https://www.mountainproject.com/whats-new-more-data?
                           type=routes&locationId=0&days=0&offset=0)
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
import datetime
import sqlite3
import time
import ssl
import re

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


# Connect to SQLite database and create database 'Routes.sqlite'
conn = sqlite3.connect('Routes-Raw.sqlite')
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

# The lowest level pages are routes.  This DB stores all the html data for the
# route pages, as well as basic route information already gathered.  The 'edit'
# column defaults to false, and will indicate that the route has been
# processed by the cleaner program.
cursor.execute('''CREATE TABLE IF NOT EXISTS Routes(
        route_info TEXT,
        url TEXT UNIQUE,
        latitude FLOAT,
        longitude FLOAT,
        area_id INTEGER,
        error INTETER,
        edit BOOLEAN DEFAULT 0)''')


def get_regions():
    """ Collects region data, the broadest category of climbing area on MP.

    'Region' refers to a state in the US, or a country outside of the US.
    Mountain Project is not well established outside of North America, so the
    number of routes in other countries is often minimal.  This function
    first finds all of the broad regions, then splits them into their areas.
    By choosing a random area that has not yet been visited - as indicated by
    the 'complete' column on the areas table - the function can quickly
    determine where it has been, and is restartable.  This requires internet
    connection, so any server error or issue with connectivity will cause the
    program to fail.

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

def get_areas():
    # Finds one random area that has not been found and pulls out the
    # information (url, name and id) that will be needed to expand it
    cursor.execute('''SELECT url, name, id FROM Areas
                              WHERE complete IS 0
                              AND error is Null
                              LIMIT 1''')
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

    The most detailed information on a route is found on its individual page,
    so the first step in grabbing the data is grabbing the URLs for the
    website.  This function iterates through the routes in an area and sends
    the URLs to the get_route_features function for final processing.

    Args:
        area_url(str): url for a specific climbing area.  MP areas can
                       contain either routes or other areas, and this function
                       only works on lowest-level areas.

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
    table = sidebar.find('div',
                         class_='max-height max-height-md-0 max-height-xs-150')
    table = table.find('table')
    routes = table.find_all('tr', id=None)
    # Gets route url and sends to get_route_features(route_url)
    for route in routes:
        route_url = route.find('a')['href']
        print('         - ', route_url)
        get_route_features(route_url, area_id, lat, long)


def get_route_features(route_url, area_id, lat, long):
    """ Gets type of route, route difficulty, route quality, and route length.

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
    if route_doc.getcode() != 200 :
        print("Error on page: ", route_doc.getcode())
        cursor.execute('UPDATE Routes SET error=? WHERE url=?',
                       (route_doc.getcode(), route_url))
        conn.commit()
    else:
        route_html = route_doc.read()
        # Parses html with BS package
        route_soup = BeautifulSoup(route_html, 'html.parser').prettify()
        cursor.execute('''
                       INSERT OR IGNORE INTO 
                       Routes(route_info, url, latitude, longitude, area_id)
                       VALUES (?, ?, ?, ?, ?)''',
                       (route_soup, route_url, lat, long, area_id))
    
        conn.commit()

error = None
while error == None:
    try:
        error = get_areas()
    except MemoryError:
        print('Memory Error at ', datetime.datetime.now().time())
        time.sleep(60)
    except:
        print('Error at '), datetime.datetime.now().time()
        time.sleep(1000)

        