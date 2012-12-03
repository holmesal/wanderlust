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
		
		pass
		
		
	def get_buildings(self):
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
			"bank",
			"hospital",
			"library",
			"church",
			"police_station",
			"fire_station",
			"school",
			"cafe",
			"bar"
		]
		
		typestring = ""
		
		for gtype in supported_types:
			if typestring == "":
				typestring += gtype
			else:
				typestring += "|"+gtype
		
		url = self.base_url + '&types='+typestring
		logging.info(url)
		
		result = urlfetch.fetch(url)
		data = json.loads(result.content)
		
		# self.parse_data(data)
		
		buildings = []
		
		for result in data["results"]:
			intersection = list(set(result["types"]).intersection(supported_types))
			subtype = intersection[0]
			geo_point = ndb.GeoPt(result["geometry"]["location"]["lat"],result["geometry"]["location"]["lng"])
			subname = result["name"]
			building = classes.Building(subtype=subtype,subname=subname,parent=self.ghash_entity.key,id=result["id"],geo_point=geo_point)
			buildings.append(building)
			logging.info(subtype)
			logging.info(subname)
		
		#store everything
		ndb.put_multi(buildings)
			
			
		if "next_page_token" in data:
			pagetoken = data["next_page_token"]
			logging.info("---RECURSION---")
			self.base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=AIzaSyCjddKUEHrVcCDqA9fqLMPUBXH0mrWPpgI&location='+str(self.center_lat)+','+str(self.center_lon)+'&radius='+str(self.radius)+'&sensor=false&pagetoken='+pagetoken
			logging.info("going to sleep")
			time.sleep(3)
			logging.info("woke up!")
			self.get_buildings()
		
		