from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from geo import geohash


class GHash(ndb.Model):
	_precision = 6
	buildings = ndb.KeyProperty()
	roads = ndb.KeyProperty()
	nature = ndb.KeyProperty()
	@property
	def name(self):
		'''
		Returns the geohash string
		'''
		# returns the geohash string
		return self.key.string_id()
	@property
	def bbox(self):
		'''
		Returns the bounding box of the ghash in form 
		lon,lat,lon,lat, (bottom left, top right)
		'''
		bbox = geohash.bbox(self.name)
		bbox_list = [
					]
		{'s': 42.3687744140625, 'e': -71.03759765625, 'w': -71.048583984375, 'n': 42.374267578125}
		
class Node(ndb.Model):
	# position of this node in the way
	idx = ndb.IntegerProperty()
	# the node's position
	geo_point = ndb.GeoPtProperty(required=True, indexed=False)
#	# the node's geohash
#	geo_hash = ndb.ComputedProperty(
#			lambda self: geohash.encode(
#				latitude = self.geo_point.lat,
#				longitude = self.geo_point.lon,
#				precision = 8
#				)
#			)

class Shape(polymodel.PolyModel):
	# has a shape definition from open maps
	nodes = ndb.StructuredProperty(Node,repeated=True)
	# does not have a shape definition from open maps
	geo_point = ndb.GeoPtProperty(indexed=False)
	geo_hash = ndb.ComputedProperty(
			lambda self: geohash.encode(
				latitude = self.geo_point.lat,
				longitude = self.geo_point.lon,
				precision = 9
				)
			)

class Road(Shape):
	road_type = ndb.StringProperty(required=True)
	road_name = ndb.StringProperty()
class Building(Shape):
	pass
class Nature(Shape):
	pass



