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
				subtype = ""
				subname = ""
				for way_child in child:
# 					logging.info(child.tag)
					if way_child.tag == 'nd':
						#save node rederence in order
						way_nodes.append(copy.copy(nodes[way_child.attrib['ref']]))
# 						logging.info(nodes[child.attrib['ref']])
					
					elif way_child.attrib['k']=='highway':
						subtype = way_child.attrib['v']
						logging.info(subtype)
					elif way_child.attrib['k']=='name':
						subname = way_child.attrib['v']
						logging.info(subname)

				#grab the required nodes and create the entity
				for idx,way_node in enumerate(way_nodes):
					way_node.idx = idx
					
				#create the road
				road = classes.Road(nodes=way_nodes,subtype=subtype,subname=subname,parent=self.ghash_entity.key,id=child.attrib["id"])
				
				#push the road onto the array
				roads.append(road)
			
		#store the array in the db
		ndb.put_multi(roads)
		
	def get_nature(self):
		url = self.base_url + '[natural=*]'
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
				subname = ""
				subtype = ""
				for way_child in child:
# 					logging.info(child.tag)
					if way_child.tag == 'nd':
						#save node rederence in order
						way_nodes.append(copy.copy(nodes[way_child.attrib['ref']]))
# 						logging.info(nodes[child.attrib['ref']])
					
					#this covers coastline, wetland, beach, etc etc
					elif way_child.attrib['k']=='natural':
						subtype = way_child.attrib['v']
						logging.info(subtype)
					
					#this covers parks (in-city)
					elif way_child.attrib['k']=='leisure':
						subtype = way_child.attrib['v']
						logging.info(subtype)
					
					elif way_child.attrib['k']=='name':
						subname = way_child.attrib['v']
						logging.info(subname)
					
				
				#grab the required nodes and create the entity
				for idx,way_node in enumerate(way_nodes):
					way_node.idx = idx
					
				#create the nature
				nature = classes.Nature(nodes=way_nodes,subtype=subtype,subname=subname,parent=self.ghash_entity.key,id=child.attrib["id"])
				
				#push the nature onto the array
				natures.append(nature)
		
		#store the array in the db
		ndb.put_multi(natures)
		
		
	def get_buildings(self):
		url = self.base_url + '[amenity=*]'
		logging.info(url)
		root = self.get_data(url)
		#empty node dict
		nodes = {}
		buildings = []
		
		'''
		Most buildings are handled as nodes, not ways. This is the geometry layer. So this function will return the building shape if it exists. We will handle the points-of-interest as NODES elsewhere. This is just for geographic shapes to aid in drawing
		'''
		
		for child in root:
			if child.tag=='node':
				#nodes should be at the top
				geo = ndb.GeoPt(child.attrib['lat'],child.attrib['lon'])
				node = classes.Node(geo_point=geo)
				nodes.update({child.attrib["id"]:node})
			elif child.tag=='way':
				way_nodes = []
				subname = ""
				subtype = ""
				for way_child in child:
# 					logging.info(child.tag)
					if way_child.tag == 'nd':
						#save node rederence in order
						way_nodes.append(copy.copy(nodes[way_child.attrib['ref']]))
# 						logging.info(nodes[child.attrib['ref']])
						
					elif way_child.attrib['k']=='amenity':
						subtype = way_child.attrib['v']
						logging.info(subtype)
					elif way_child.attrib['k']=='name':
						subname = way_child.attrib['v']
						logging.info(subname)
					
				
				#grab the required nodes and create the entity
				for idx,way_node in enumerate(way_nodes):
					way_node.idx = idx
					
				#create the building
				building = classes.Building(nodes=way_nodes,subtype=subtype,subname=subname,parent=self.ghash_entity.key,id=child.attrib["id"])
				
				#push the building onto the array
				buildings.append(building)
				
# 		logging.info(buildings)
		
		#store the array in the db
		ndb.put_multi(buildings)
		
		
		
	def get_leisure(self):
		url = self.base_url + '[leisure=*]'
		logging.info(url)
		root = self.get_data(url)
		#empty node dict
		nodes = {}
		leisures = []
		
		
		for child in root:
			if child.tag=='node':
				#nodes should be at the top
				geo = ndb.GeoPt(child.attrib['lat'],child.attrib['lon'])
				node = classes.Node(geo_point=geo)
				nodes.update({child.attrib["id"]:node})
			elif child.tag=='way':
				way_nodes = []
				subname = ""
				subtype = ""
				for way_child in child:
# 					logging.info(child.tag)
					if way_child.tag == 'nd':
						#save node rederence in order
						way_nodes.append(copy.copy(nodes[way_child.attrib['ref']]))
# 						logging.info(nodes[child.attrib['ref']])
						
					elif way_child.attrib['k']=='leisure':
						subtype = way_child.attrib['v']
						logging.info(subtype)
					elif way_child.attrib['k']=='name':
						subname = way_child.attrib['v']
						logging.info(subname)
					
				
				#grab the required nodes and create the entity
				for idx,way_node in enumerate(way_nodes):
					way_node.idx = idx
					
				#create the building
				leisure = classes.Leisure(nodes=way_nodes,subtype=subtype,subname=subname,parent=self.ghash_entity.key,id=child.attrib["id"])
				
				#push the building onto the array
				leisures.append(leisure)
				
# 		logging.info(buildings)
		
		#store the array in the db
		ndb.put_multi(leisures)
