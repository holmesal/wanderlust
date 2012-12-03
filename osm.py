import webapp2
import logging
import copy



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
		
		self.base_url = 'http://www.overpass-api.de/api/xapi?*[bbox='+str(bbox[0])+','+str(bbox[1])+','+str(bbox[2])+','+str(bbox[3])+']'
		
		
		
		#build the request url
# 		self.url = 'http://www.overpass-api.de/api/xapi?*[bbox='+str(bbox[0])+','+str(bbox[1])+','+str(bbox[2])+','+str(bbox[3])+']'+filt_string
		
		logging.info(self.base_url)
		
	def get_data(self,url):
		result = urlfetch.fetch(url)
		
		root = ET.fromstring(result.content)
		return root
		
	def get_roads(self):
		url = self.base_url + '[highway=*]'
		root = self.get_data(url)
		#empty node dict
		nodes = {}
		roads = []
		
		for child in root:
			if child.tag=='node':
				#nodes should be at the top
				geo = ndb.GeoPt(child.attrib['lat'],child.attrib['lon'])
				node = classes.Node(geo_point=geo)
				nodes.update({child.attrib["id"]:node})
			elif child.tag=='way':
				way_nodes = []
				road_type = ""
				road_name = ""
				for way_child in child:
# 					logging.info(child.tag)
					if way_child.tag == 'nd':
						#save node rederence in order
						way_nodes.append(copy.copy(nodes[way_child.attrib['ref']]))
# 						logging.info(nodes[child.attrib['ref']])
					
					elif way_child.attrib['k']=='highway':
						road_type = way_child.attrib['v']
					elif way_child.attrib['k']=='name':
						road_name = way_child.attrib['v']
# 					else:
# 						logging.info(child.attrib)
				
				#grab the required nodes and create the entity
				for idx,way_node in enumerate(way_nodes):
					way_node.idx = idx
				for node in way_nodes:
					logging.info(node.idx)
					
				#create the road
				road = classes.Road(nodes=way_nodes,road_type=road_type,road_name=road_name,parent=self.ghash_entity.key,id=child.attrib["id"])
				
				#push the road onto the array
				roads.append(road)
			
		#store the array in the db
		ndb.put_multi(roads)
		
	def get_nature(self):
		pass
		
	def get_buildings(self):
		pass
	

				

class OsmHandler(webapp2.RequestHandler):
	def get(self):
		geo_point = 42.3697785,-71.0391343 # maverick square
		ghash = geohash.encode(geo_point[0], geo_point[1], classes.GHash._precision)
		
		geo_hash_entity = classes.GHash.get_or_insert(ghash)
		osm = Osm(geo_hash_entity,"roads")
		osm.getdata()

app = webapp2.WSGIApplication([('/osm',OsmHandler)])