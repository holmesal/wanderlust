from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from geo import geohash
import osm
import gplaces
import logging
import vibes


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
		
	def populate(self):
		'''
		Create an Osm entity and populate with roads, etc
		Then create a Gmaps entity and populate with buildings and places, etc
		'''
		try:
			# open street maps
			tile = osm.Osm(self)
			nature_count = tile.get_nature()
			roads_count = tile.get_roads()
			buildings_count = tile.get_buildings()
			leisure_count = tile.get_leisure()
			
			places = gplaces.Gplaces(self)
			places_count = places.get_buildings()
			
			logging.info(nature_count)
			logging.info(roads_count)
			logging.info(buildings_count)
			logging.info(leisure_count)
			logging.info(places_count)
		except Exception,e:
			logging.error(str(e))
	
	def calculate_vibe(self):
		'''
		Figure out how many roads, buildings, etc are in this geohash
		Use this to generate a probability dictionary for this geohash
		'''
		
		count_roads = Road.query(ancestor=self.key).count()
		count_nature = Nature.query(ancestor=self.key).count()
		
		
class Node(ndb.Model):
	# position of this node in the way
	idx = ndb.IntegerProperty(indexed = False, default = 0)
	# the node's position
	geo_point = ndb.GeoPtProperty(required=True, indexed=False)
	def package(self):
		return {
			'idx' : self.idx,
			'geo_point' : str(self.geo_point)
			}


class Ground(polymodel.PolyModel):
	'''
	Root class
	Stuff thats on the ground layer. 
	'''
	# has a shape definition from open maps
	nodes = ndb.LocalStructuredProperty(Node,repeated=True)
	def package(self,packaged={}):
		packaged.update({
						'id' : self.key.id(),
						'types' : self.class_,
						'nodes' : [node.package() for node in self.nodes]
						})
		try:
			subtype = packaged['subtype']
			packaged['types'].append(subtype)
			del packaged['subtype']
		except:
			pass
		return packaged

class Road(Ground):
	'''
	Never heard of a road. What is it?
	'''
	subtype = ndb.StringProperty(required=True)
	subname = ndb.StringProperty()
	def package(self,packaged={}):
		packaged.update({
						'subtype' : self.subtype,
						'subname' : self.subname
						})
		return super(Road,self).package(packaged)
class Leisure(Ground):
	'''
	outdoor entertainment. man-made. think parks, playgrounds, etc
	'''
	subtype = ndb.StringProperty(required=True)
	subname = ndb.StringProperty()
	def package(self,packaged={}):
		packaged.update({
						'subtype' : self.subtype,
						'subname' : self.subname
						})
		return super(Leisure,self).package(packaged)
		
class Nature(Ground):
	'''
	Completely natural features - not man made (okay, beaches can be manmade, but you know what i mean).
	Think coastline, etc
	'''
	subtype = ndb.StringProperty(required=True)
	subname = ndb.StringProperty()
	def package(self,packaged={}):
		packaged.update({
				'subtype' : self.subtype,
				'subname' : self.subname
				})
		return super(Nature,self).package(packaged)

class BuildingFootprint(Ground):
	'''
	outlines of buildings. only exists in some places
	'''
	subtype = ndb.StringProperty(required=True)
	subname = ndb.StringProperty()
	def package(self):
		packaged = {
				'subtype' : self.subtype,
				'name' : self.subname
				}
		return super(BuildingFootprint,self).package(packaged)



class Structure(polymodel.PolyModel):
	'''
	Root class
	Anything real-world entity that exists above the ground layer
	'''
	
	geo_point = ndb.GeoPtProperty(required=True, indexed=False)		#refers to the center of the structure
	def package(self,packaged={}):
		packaged.update({
						'id' : self.key.id(),
						'types' : self.class_,
						'geo_point' : str(self.geo_point)
						})
		try:
			subtype = packaged['subtype']
			packaged['types'].append(subtype)
			del packaged['subtype']
		except:
			pass
		return packaged
		
	
class Building(Structure):
	'''
	A traditional building. You know, suburbia.
	
	'''
	subtype = ndb.StringProperty(required=True)	#hospital,school,etc
	subname = ndb.StringProperty()
	def package(self):
		packaged = {}
		packaged.update({
						'subtype' : self.subtype,
						'subname' : self.subname
						})
		return super(Building,self).package(packaged)
