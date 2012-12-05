import webapp2
import logging
import jinja2
import os
import json
import utils
from geo import geohash

from google.appengine.ext import ndb
import classes

class WorldHandler(utils.BaseHandler):
	def get(self):
# 		geo_point = [42.358431,-71.059773]
		geo_point = [42.3617863, -71.1359041]
		ghash = geohash.encode(geo_point[0], geo_point[1], classes.GHash._precision)
		geo_hash_entity = classes.GHash.get_or_insert(ghash)
		geo_hash_entity.populate()
		self.view_geohash(ghash)
		


app = webapp2.WSGIApplication([('/world',WorldHandler)])