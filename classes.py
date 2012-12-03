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
		
class Node(ndb.Model):
	# position of this node in the way
	idx = ndb.IntegerProperty(indexed = False)
	# the node's position
	geo_point = ndb.GeoPtProperty(required=True, indexed=False)
	def package(self):
		return self.to_dict()

class Shape(polymodel.PolyModel):
	# has a shape definition from open maps
	nodes = ndb.LocalStructuredProperty(Node,repeated=True)
	
	def package(self):
		return self.to_dict()
	
class Point(polymodel.PolyModel):
	geo_point = ndb.GeoPtProperty(required=True, indexed = False)
	def package(self):
		return self.to_dict()

class Road(Shape):
	road_type = ndb.StringProperty(required=True)
	road_name = ndb.StringProperty()
class Building(Shape):
	building_type = ndb.StringProperty(required=True)
	building_name = ndb.StringProperty()
class Nature(Shape):
	nature_type = ndb.StringProperty(required=True)
	nature_name = ndb.StringProperty()
class Water(Shape):
	water_type = ndb.StringProperty(required=True)
	water_name = ndb.StringProperty()


