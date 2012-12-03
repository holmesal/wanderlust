import logging
import json
import time

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

import classes
from geo import geohash
import geo_utils


class Gplaces(object):
	
	def __init__(self,ghash_entity):
	
		assert type(ghash_entity) == classes.GHash,type(ghash_entity)
		self.ghash_entity = ghash_entity
		
		bbox = self.ghash_entity.bbox
		
		self.radius = geo_utils.distance_between_points(bbox[1],bbox[0],bbox[3],bbox[2])/2
		
		self.center_lon = (bbox[0]+bbox[2])/2
		self.center_lat = (bbox[1]+bbox[3])/2
		
		self.base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=AIzaSyCjddKUEHrVcCDqA9fqLMPUBXH0mrWPpgI&location='+str(self.center_lat)+','+str(self.center_lon)+'&radius='+str(self.radius)+'&sensor=false'
		
	def parse_data(self,data):
		
		for result in data["results"]:
			logging.info(result["name"])
			logging.info(result["types"])
		
		
	def get_data(self):
# 		supported_types = [
# 			"bank",
# 			"bar",
# 			"bus_station",
# 			"cafe",
# 			"cemetary",
# 			"church",
# 			"convenience_store",
# 			"establishment",
# 			"fire_station",
# 			"food",
# 			"hospital",
# 			"library",
# 			"lodging",
# 			"museum",
# 			"night_club",
# 			"park",
# 			"police",
# 			"post_office",
# 			"restaurant",
# 			"school",
# 			"store",
# 			"subway_station",
# 			"train_station"
# 		]

		supported_types = [
			"bus_station",
			"subway_station",
			"train_station"
		]
		
		typestring = "park"
		for gtype in supported_types:
			typestring += "|"+gtype
		
		url = self.base_url + '&types='+typestring
		
		
		
		
		logging.info(url)
		
		result = urlfetch.fetch(url)
		
		data = json.loads(result.content)
		
		self.parse_data(data)
			
		if "next_page_token" in data:
			pagetoken = data["next_page_token"]
			logging.info("---RECURSION---")
			self.base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=AIzaSyCjddKUEHrVcCDqA9fqLMPUBXH0mrWPpgI&location='+str(self.center_lat)+','+str(self.center_lon)+'&radius='+str(self.radius)+'&sensor=false&pagetoken='+pagetoken
			logging.info("going to sleep")
			time.sleep(3)
			logging.info("woke up!")
			self.get_data()
		
		