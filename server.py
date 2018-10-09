#!/usr/bin/env python

###############################################################################
#                    Import Required Libraries.                               #
###############################################################################
import json
import os

import ee
import webapp2

###############################################################################
#                               Initialization.                               #
###############################################################################

ee.Initialize()

# set the collection ID
jrc_dataset = ee.ImageCollection('JRC/GSW1_0/MonthlyHistory')
# Note
# Band Name	  Label
# water	      0 = no data
#             1 = not water
#             2 = water

# Define country names
#countries_names = ['Myanmar (Burma)', 'Thailand', 'Laos', 'Vietnam', 'Cambodia']
countries_names = ['Vietnam']
# import the country feature collection
countries = ee.FeatureCollection('ft:1tdSwUL7MVpOauSgRzqVTOwdfy17KDbw-1d9omPw')
# find the countries in the country list
geometry = countries.filter(ee.Filter.inList('Country', countries_names)).geometry()

# Or you can defined geometry from polygon as well
coordinates = [99.63, 14.37, 100.09, 14.77, 100.38, 14.33, 99.83, 14.05];
#geometry = ee.Geometry.Polygon(coordinates);

palette = 'c10000,d742f4,001556,b7d2f7'

###############################################################################
#                             Web request handlers.                           #
###############################################################################

class MainHandler(webapp2.RequestHandler):
    """A servlet to handle requests to load the main web page."""
    
    def get(self):
        self.response.headers.add_header('Access-Control-Allow-Origin', '*')
        start = self.request.get('start', '2000-01-01')
        end = self.request.get('end', '2012-12-31')
        mapid = get_map(start, end, True)
        template_values = {
            'eeMapId': mapid['mapid'],
            'eeMapToken': mapid['token']
        }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(template_values))

class DownloadHandler(webapp2.RequestHandler):

    def get(self):
        self.response.headers.add_header('Access-Control-Allow-Origin', '*')
        start = self.request.get('start', '2000-01-01')
        end = self.request.get('end', '2012-12-31')
        image = get_map(start, end, False)
        download_url = get_download_url(image)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(download_url))

##############################################################################
# Define webapp2 routing from URL paths to web request handlers.             #
###############################################################################

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/download-url', DownloadHandler),
])

###############################################################################
#                                   Helper Functions                          #
###############################################################################

def get_map(start_date, end_date, get_id):

    # Filter to region and date
    filtered_jrc = jrc_dataset.filterBounds(geometry).filterDate(start_date, end_date)

    # calculate total number of valid observations
    def calc_obs(img):
        # observation is img > 0
        obs = img.gt(0)
        return ee.Image(obs).set('system:time_start', img.get('system:time_start'))

    # calculate the number of times water
    def calc_water(img):
        water = img.select('water').eq(2)
        return ee.Image(water).set('system:time_start', img.get('system:time_start'))

    observations = filtered_jrc.map(calc_obs)
    
    water = filtered_jrc.map(calc_water)

    # sum the totals
    total_obs = ee.Image(ee.ImageCollection(observations).sum().toFloat())
    total_water = ee.Image(ee.ImageCollection(water).sum().toFloat())

    # calculate the percentage of total water
    water_percent = total_water.divide(total_obs).multiply(100)

    # make a mask
    mask = water_percent.gt(1)
    water_percent = water_percent.updateMask(mask)

    # clip the result
    water_percent = water_percent.clip(geometry)

    if get_id:
        return water_percent.getMapId({
            'min': '0',
            'max': '100',
            'bands': 'water',
            'palette' : palette
        })
    else:
        return water_percent

def get_download_url(image):

    return image.getDownloadURL({
        'scale': 30,
        'region': coordinates
    })

###############################################################################
#                          Bootstrap the application                          #
###############################################################################

def main():
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='8001')
    
if __name__ == '__main__':
    main()
