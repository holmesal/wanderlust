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
	idx = ndb.IntegerProperty(indexed = False, default = 0)
	# the node's position
	geo_point = ndb.GeoPtProperty(required=True, indexed=False)
	def package(self):
		return self.to_dict()

class Point(polymodel.PolyModel):
	geo_point = ndb.GeoPtProperty(required=True, indexed = False)
	def package(self):
		return self.to_dict()

class Shape(polymodel.PolyModel):
	# has a shape definition from open maps
	nodes = ndb.LocalStructuredProperty(Node,repeated=True)
	
	def package(self):
		return self.to_dict()

class Ground(Shape):
	pass
class Road(Ground):
	'''
	
	'''
	subtype = ndb.StringProperty(required=True)
	subname = ndb.StringProperty()
class Leisure(Ground):
	'''
	Urban wildlife
	'''
	subtype = ndb.StringProperty(required=True)
	subname = ndb.StringProperty()
class Nature(Ground):
	'''
	Wildlife stuff
	'''
	subtype = ndb.StringProperty(required=True)
	subname = ndb.StringProperty()

	class Building(Shape):
		'''
		
		'''
		subtype = ndb.StringProperty(required=True)
		subname = ndb.StringProperty()

