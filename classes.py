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
	Urban wildlife
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
	Wildlife wildlife
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
