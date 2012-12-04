import webapp2
import logging
import jinja2
import os
import json

from google.appengine.ext import ndb

from geo import geohash
import classes


class WorldHandler(webapp2.RequestHandler):
	def get(self):
		geo_point = 42.3697785,-71.0391343 # maverick square
		ghash = geohash.encode(geo_point[0], geo_point[1], classes.GHash._precision)
		ent = classes.GHash.get_or_insert(ghash)
		
		grounds = classes.Ground.query(ancestor=ent.key).fetch(None)
		
		features = {"features":[]}
		
		for ground in grounds:
			if ground.subtype != "alonso":
# 				logging.info(ground.nodes)
				coords = []
				for node in ground.nodes:
					coord = [node.geo_point.lon,node.geo_point.lat]
					coords.append(coord)
# 				logging.info(coords)
				feature = {
					"type"		:	"Feature",
					"id"		:	ground.key.string_id(),
					"geometry"	:	{
						"type"			:	"LineString",
						"coordinates"	:	coords,
					},
					"properties":	{
						"popupContent"	:	ground.subname + ':::' + ground.subtype
# 						"type"			:	ground.subtype,
# 						"name"			:	ground.subname
					}
				}
# 				logging.info(json.dumps(feature))
				features["features"].append(json.dumps(feature))

		
		jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
		template = jinja_environment.get_template('templates/world.html')
 		self.response.out.write(template.render(features))
		


app = webapp2.WSGIApplication([('/world',WorldHandler)])