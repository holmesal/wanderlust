import webapp2
import logging



from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import xml.etree.ElementTree as ET

import classes
from geo import geohash


class Osm(object):
	
	def __init__(self,ghash_entity,layer):
		assert type(ghash_entity) == classes.GHash,type(ghash_entity)
		self.ghash_entity = ghash_entity

		bbox = self.ghash_entity.bbox

		assert layer in ["roads","nature","buildings"], "Must pass a valid layer string: roads, nature, or buildings"
		self.layer = layer
		
#		bbox = geohash.bbox(ghash_entity.name)
##		assert False, bbox
#		bbox = [-71.0442,42.3622,-71.027,42.3697]
		assert type(bbox) == list, 'Must pass in bounding box as a 4-element list - lon,lat,lon,lat'
		
		base_url = 'http://www.overpass-api.de/api/xapi?*[bbox='+str(bbox[0])+','+str(bbox[1])+','+str(bbox[2])+','+str(bbox[3])+']'
		
		if layer == "roads":
			self.url = base_url + '[highway=*]'
		elif layer == "nature":
			self.url = base_url + '[landcover=grass]'
		elif layer == "buildings":
			self.url = base_url
		
		#build the request url
# 		self.url = 'http://www.overpass-api.de/api/xapi?*[bbox='+str(bbox[0])+','+str(bbox[1])+','+str(bbox[2])+','+str(bbox[3])+']'+filt_string
		
		logging.info(self.url)
		
	def getdata(self):
		result = urlfetch.fetch(self.url)
		
		self.xml = result.content
		self.root = ET.fromstring(result.content)
		
		if self.layer == "roads":
			self.get_roads()
		elif self.layer == "nature":
			self.get_nature()
		elif self.layer == "buildings":
			self.get_buildings()
		
	def get_roads(self):
	
		#empty node dict
		nodes = {}
		roads = []
		
		for child in self.root:
			if child.tag=='node':
				#nodes should be at the top
				geo = ndb.GeoPt(child.attrib['lat'],child.attrib['lon'])
				node = classes.Node(geo_point=geo)
				nodes.update({child.attrib["id"]:node})
			elif child.tag=='way':
				way_nodes = []
				road_type = ""
				road_name = ""
				for child in child:
# 					logging.info(child.tag)
					if child.tag == 'nd':
						#save node rederence in order
						way_nodes.append(nodes[child.attrib['ref']])
# 						logging.info(nodes[child.attrib['ref']])
					
					elif child.attrib['k']=='highway':
						road_type = child.attrib['v']
					elif child.attrib['k']=='name':
						road_name = child.attrib['v']
# 					else:
# 						logging.info(child.attrib)
				
				#grab the required nodes and create the entity
				for idx,way_node in enumerate(way_nodes):
					way_node.idx = idx
# 					logging.info(idx)
					
				#create the road
# 				road = classes.Road(nodes=way_nodes,road_type=road_type,road_name=road_name,parent=self.ghashentity)
				road = classes.Road(nodes=way_nodes,road_type=road_type,road_name=road_name,parent=self.ghash_entity.key)
				
				#push the road onto the array
				roads.append(road)
			
		#store the array in the db
		ndb.put_multi(roads)
		logging.info(roads)
		
	def get_nature(self):
		pass
		
	def get_buildings(self):
		pass
	

				

class OsmHandler(webapp2.RequestHandler):
	def get(self):
		geo_point = 42.3697785,-71.0391343 # maverick square
		ghash = geohash.encode(geo_point[0], geo_point[1], classes.GHash._precision)
		
		geo_hash_entity = classes.GHash.get_or_insert(ghash)
		osm = Osm(geo_hash_entity,"nature")
		osm.getdata()

app = webapp2.WSGIApplication([('/osm',OsmHandler)])