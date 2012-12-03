from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from geo import geohash


class GHash(ndb.Model):
	_precision = 6
	@property
	def name(self):
		'''
		@return: The geo_hash string that is the id of this entity
		@rtype: str
		'''
		return self.key.string_id()
	@property
	def bbox(self):
		'''
		Returns the bounding box of the ghash in form 
		lon,lat,lon,lat, (bottom left, top right)
		
		@return: the bounding box of the ghash in form: lon,lat,lon,lat, (bottom left, top right)
		@rtype: list
		'''
		bbox = geohash.bbox(self.name)
		bbox_list = [
					bbox['w'],
					bbox['s'],
					bbox['e'],
					bbox['n']
					]
		return bbox_list
	
	@property
	def refresh(self):
		'''
		remove everything inside this geohash, and re-populate
		'''
		pass
		
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
class Point(polymodel.PolyModel):
	geo_point = ndb.GeoPtProperty(required=True, indexed = False)
#	geo_hash = ndb.ComputedProperty(
#			lambda self: geohash.encode(
#				latitude = self.geo_point.lat,
#				longitude = self.geo_point.lon,
#				precision = 8
#				)
#			)

class Road(Shape):
	subtype = ndb.StringProperty(required=True)
	subname = ndb.StringProperty()
class Leisure(Shape):
	subtype = ndb.StringProperty(required=True)
	subname = ndb.StringProperty()
class Building(Shape):
	subtype = ndb.StringProperty(required=True)
	subname = ndb.StringProperty()
class Nature(Shape):
	subtype = ndb.StringProperty(required=True)
	subname = ndb.StringProperty()



