import webapp2
import logging
import copy

import osm
import gplaces
from geo import geohash
import classes
import utils

class OsmHandler(utils.BaseHandler):
	def get(self):
		geo_points = []
		geo_points.append((42.3697785,-71.0391343)) # maverick square
		geo_points.append((42.358431,-71.059773)) # downtown
		geo_points.append((42.383992,-71.010427)) # costal
		
		successes = []
		for geo_point in geo_points:
			try:
				ghash = geohash.encode(geo_point[0], geo_point[1], classes.GHash._precision)
				
				geo_hash_entity = classes.GHash.get_or_insert(ghash)
				tile = osm.Osm(geo_hash_entity) 
				tile.get_nature()
				tile.get_roads()
				tile.get_buildings()
				tile.get_leisure()
			except Exception,e:
				logging.error(str(e))
			else:
				logging.info('fetch success for '+str(geo_point))
				successes.append(geo_point)
		self.response.out.write('Done!')
		self.say(successes)
		

class GplacesHandler(webapp2.RequestHandler):
	def get(self):
		geo_point = 42.3697785,-71.0391343 # maverick square
		ghash = geohash.encode(geo_point[0], geo_point[1], classes.GHash._precision)
		geo_hash_entity = classes.GHash.get_or_insert(ghash)
		
		tile = gplaces.Gplaces(geo_hash_entity)
		tile.get_buildings()


app = webapp2.WSGIApplication([('/getdata/osm',OsmHandler),
								('/getdata/gplaces',GplacesHandler)])
