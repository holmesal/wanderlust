from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel

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

class Tree(Structure):
	'''
	Any sort of tree.
	You can't move through these
	'''
	pass
	
class Dungeon(Structure):
	'''
	OMG it's a dungeon
	'''
	pass
	
class Grass(Structure):
	'''
	Not the herbal kind...
	'''
	pass
