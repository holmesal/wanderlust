from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from geo import geohash


class GHash(ndb.Model):
	buildings = ndb.KeyProperty()
	roads = ndb.KeyProperty()
	nature = ndb.KeyProperty()

class Node(ndb.Model):
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

class Road(ndb.Model):
	# the actual nodes
	nodes = ndb.StructuredProperty(Node,repeated=True)

class Building(ndb.Model):
	nodes = ndb.StructuredProperty(Node,repeated=True)
	# the building does not have a shape definition from open maps
	geo_point = ndb.GeoPtProperty(indexed=False)
	# the node's geohash
	geo_hash = ndb.ComputedProperty(
			lambda self: geohash.encode(
				latitude = self.geo_point.lat,
				longitude = self.geo_point.lon,
				precision = 9
				)
			)
class Nature(ndb.Model):
	# the building has a shape definition from open maps
	nodes = ndb.StructuredProperty(Node,repeated=True)
	# the building does not have a shape definition from open maps
	geo_point = ndb.GeoPtProperty(indexed=False)
	# the node's geohash
	geo_hash = ndb.ComputedProperty(
			lambda self: geohash.encode(
				latitude = self.geo_point.lat,
				longitude = self.geo_point.lon,
				precision = 9
				)
			)