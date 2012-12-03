import logging

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

import classes
from geo import geohash

class Gplaces(object):
	
	def __init__(self,ghash_entity):
		geo_point = self.ghash_entity.geo_point
		
		self.base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
		
	def get_data(self):
		