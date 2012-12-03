import logging
import copy

from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import xml.etree.ElementTree as ET

import classes
from geo import geohash


class Osm(object):
	
	def __init__(self,ghash_entity):
		assert type(ghash_entity) == classes.GHash,type(ghash_entity)
		self.ghash_entity = ghash_entity

		bbox = self.ghash_entity.bbox

		assert type(bbox) == list, 'Must pass in bounding box as a 4-element list - lon,lat,lon,lat'
		
		self.base_url = 'http://www.overpass-api.de/api/xapi?*[bbox='+str(bbox[0])+','+str(bbox[1])+','+str(bbox[2])+','+str(bbox[3])+']'
		
	def get_data(self,url):
		
		result = urlfetch.fetch(url)
		root = ET.fromstring(result.content)
		
		return root
		
	def get_roads(self):
		url = self.base_url + '[highway=*]'
		logging.info(url)
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
						logging.info(road_name)
					elif way_child.attrib['k']=='name':
						road_name = way_child.attrib['v']
						logging.info(road_type)

				#grab the required nodes and create the entity
				for idx,way_node in enumerate(way_nodes):
					way_node.idx = idx
					
				#create the road
				road = classes.Road(nodes=way_nodes,road_type=road_type,road_name=road_name,parent=self.ghash_entity.key,id=child.attrib["id"])
				
				#push the road onto the array
				roads.append(road)
			
		#store the array in the db
		ndb.put_multi(roads)
		
	def get_nature(self):
		url = self.base_url + '[leisure=*]'
		logging.info(url)
		root = self.get_data(url)
		#empty node dict
		nodes = {}
		natures = []
		
		for child in root:
			if child.tag=='node':
				#nodes should be at the top
				geo = ndb.GeoPt(child.attrib['lat'],child.attrib['lon'])
				node = classes.Node(geo_point=geo)
				nodes.update({child.attrib["id"]:node})
			elif child.tag=='way':
				way_nodes = []
				nature_name = ""
				nature_type = ""
				for way_child in child:
# 					logging.info(child.tag)
					if way_child.tag == 'nd':
						#save node rederence in order
						way_nodes.append(copy.copy(nodes[way_child.attrib['ref']]))
# 						logging.info(nodes[child.attrib['ref']])
						
					elif way_child.attrib['k']=='leisure':
						nature_type = way_child.attrib['v']
						logging.info(nature_type)
					elif way_child.attrib['k']=='name':
						nature_name = way_child.attrib['v']
						logging.info(nature_name)
					
				
				#grab the required nodes and create the entity
				for idx,way_node in enumerate(way_nodes):
					way_node.idx = idx
					
				#create the road
				nature = classes.Road(nodes=way_nodes,parent=self.ghash_entity.key,id=child.attrib["id"])
				
				#push the road onto the array
				natures.append(nature)
		
		
		
	def get_buildings(self):
		pass
