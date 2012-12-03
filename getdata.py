import webapp2
import logging
import copy

import osm
from geo import geohash
import classes

class GetDataHandler(webapp2.RequestHandler):
	def get(self):
		geo_point = 42.3697785,-71.0391343 # maverick square
		ghash = geohash.encode(geo_point[0], geo_point[1], classes.GHash._precision)
		
		geo_hash_entity = classes.GHash.get_or_insert(ghash)
		tile = osm.Osm(geo_hash_entity)
		tile.get_nature()

app = webapp2.WSGIApplication([('/getdata',GetDataHandler)])