import webapp2
import logging
import copy
import osm
import gplaces
from geo import geohash
import classes
import utils
from datetime import datetime
geo_points = []
# geo_points.append((42.3697785,-71.0391343)) # maverick square
# geo_points.append((42.358431,-71.059773)) # downtown
# geo_points.append((42.383992,-71.010427)) # costal
geo_points.append((42.3617863, -71.1359041)) # 260 everett str
class OsmHandler(utils.BaseHandler):
	def get(self):
		t0 = datetime.now()
		self.set_plaintext()

		successes = []
		for geo_point in geo_points:
			try:
				ghash = geohash.encode(geo_point[0], geo_point[1], classes.GHash._precision)
				
				geo_hash_entity = classes.GHash.get_or_insert(ghash)
# 				geo_hash_entity = classes.GHash.get_or_insert('drt2zp')
				# tile = osm.Osm(geo_hash_entity) 
# 				tile.get_nature()
# 				tile.get_roads()
# 				tile.get_buildings()
# 				tile.get_leisure()
				geo_hash_entity.populate()
				self.view_geohash(geo_hash_entity.name)
				
			except Exception,e:
				utils.log_error(e)
			else:
				logging.info('fetch success for '+str(geo_point))
				successes.append(geo_point)
# 		self.response.out.write('Done!')
# 		self.say(successes)
# 		self.say(datetime.now() - t0)
# 		geo_point = 42.3697785,-71.0391343 # maverick square
# # 		geo_point = 42.358431,-71.059773 # downtown
# # 		geo_point = 42.383992,-71.010427 # costal
# 		ghash = geohash.encode(geo_point[0], geo_point[1], classes.GHash._precision)
		

class GplacesHandler(utils.BaseHandler):
	def get(self):
		self.set_plaintext()
		t0 = datetime.now()
#		geo_point = 42.3697785,-71.0391343 # maverick square
		successes = []
		for geo_point in geo_points:
			try:
				ghash = geohash.encode(geo_point[0], geo_point[1], classes.GHash._precision)
				geo_hash_entity = classes.GHash.get_or_insert(ghash)
				
				tile = gplaces.Gplaces(geo_hash_entity)
				tile.get_buildings()
			except Exception,e:
				logging.error(str(e))
			else:
				logging.info('fetch success for '+str(geo_point))
				successes.append(geo_point)
		self.say(successes)
		self.say(datetime.now() - t0)


app = webapp2.WSGIApplication([('/getdata/osm',OsmHandler),
								('/getdata/gplaces',GplacesHandler)])
