from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from geo import geohash


class GHash(ndb.Model):
	center = ndb.GeoPtProperty(required=True)
	corners = ndb.ComputedProperty(lambda self: geohash.bbox(self.center[:5]))

class Node(ndb.Model):
	# the numeric openmaps id for this node
	id = ndb.IntegerProperty(required=True)
	# position of this node in the way
	idx = ndb.IntegerProperty(required=True)
	# the node's position
	geo_point = ndb.GeoPtProperty(required=True, indexed=False)
	# the node's geohash
	geo_hash = ndb.ComputedProperty(
			lambda self: geohash.encode(
				latitude = self.geo_point.lat,
				longitude = self.geo_point.lon,
				precision = 8
				)
			)

class Shape(polymodel.PolyModel):
	nodes = ndb.StructuredProperty(Node,repeated=True)
	
class Road(ndb.Model):
	pass
class Building(ndb.Model):
	pass