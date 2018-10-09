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
IMAGE_COLLECTION = ee.ImageCollection('JRC/GSW1_0/MonthlyHistory')

# Define country names
country_names = ['Myanmar (Burma)', 'Thailand', 'Laos', 'Vietnam', 'Cambodia']
# import the country feasture collection
countries = ee.FeatureCollection('ft:1tdSwUL7MVpOauSgRzqVTOwdfy17KDbw-1d9omPw')
# find the countries in the country list
mekongCountries = countries.filter(ee.Filter.inList('Country', country_names));
# Get the geometry of the countries
mekongRegion = mekongCountries.geometry()

###############################################################################
#                             Web request handlers.                           #
###############################################################################

class MainHandler(webapp2.RequestHandler):
    """A servlet to handle requests to load the main web page."""
    
    def get(self):
        self.response.headers.add_header('Access-Control-Allow-Origin', '*')
        start = self.request.get('start', '2000-01-01')
        end = self.request.get('end', '2012-12-31')
        mapid = updateMap(start, end)
        template_values = {
            'eeMapId': mapid['mapid'],
            'eeMapToken': mapid['token']
        }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(template_values))

##############################################################################
# Define webapp2 routing from URL paths to web request handlers.             #
###############################################################################

app = webapp2.WSGIApplication([
    ('/', MainHandler),
])

###############################################################################
#                                   Helper Functions                          #
###############################################################################

def updateMap(startDate, endDate):


    myjrc = IMAGE_COLLECTION.filterBounds(mekongRegion).filterDate(startDate, endDate)
    
    # calculate total number of observations
    def calcObs(img):
        # observation is img > 0
        obs = img.gt(0)
        return ee.Image(obs).set('system:time_start', img.get('system:time_start'));  
    
    # calculate the number of times water
    def calcWater(img):
        water = img.select('water').eq(2);
        return ee.Image(water).set('system:time_start', img.get('system:time_start'));
        
    observations = myjrc.map(calcObs)
    
    water = myjrc.map(calcWater)
    
    # sum the totals
    totalObs = ee.Image(ee.ImageCollection(observations).sum().toFloat());
    totalWater = ee.Image(ee.ImageCollection(water).sum().toFloat());
    
    # calculate the percentage of total water
    returnTime = totalWater.divide(totalObs).multiply(100)
    
    # make a mask
    Mask = returnTime.gt(1)
    returnTime = returnTime.updateMask(Mask)
    
    # clip the result
    returnTime = returnTime.clip(mekongRegion)
    
    return returnTime.getMapId({
        'min': '0',
        'max': '100',
        'bands': 'water',
        'palette' : 'c10000,d742f4,001556,b7d2f7'
    })

###############################################################################
#                          Bootstrap the application                          #
###############################################################################

def main():
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='8001')
    
if __name__ == '__main__':
    main()
