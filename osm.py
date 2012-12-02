import webapp2
import logging



from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import xml.etree.ElementTree as ET

# import classes


class Osm(object):
	
	def __init__(self,bbox,filters=None):
	
		assert type(bbox) == list, 'Must pass in bounding box as a 4-element list - lon,lat,lon,lat'
		
		filt_string = ''
		
		if filters:
			assert type(filters) == dict, 'Must pass in filters as a dictionary'
			
			for filt in filters:
				filt_string = filt_string + '['+filt+'='+filters[filt]+']'
				
		
		#build the request url
		self.url = 'http://www.overpass-api.de/api/xapi?*[bbox='+str(bbox[0])+','+str(bbox[1])+','+str(bbox[2])+','+str(bbox[3])+']'+filt_string
		
		logging.info(self.url)
		
		
	def getdata(self):
		result = urlfetch.fetch(self.url)
		
		self.xml = result.content
		self.root = ET.fromstring(result.content)
		
		self.parse()
	
	def parse(self):
	
		#empty node dict
		nodes = {}
		
		for child in self.root:
			if child.tag=='node':
				#nodes should be at the top
				geo = ndb.GeoPt(child.attrib['lat'],child.attrib['lon'])
				node = classes.Node(geo_point=geo)
				nodes.extend({child.attrib["id"]:node})
			elif child.tag=='way':
				nodes = []
				for child in child:
					logging.info(child.tag)
					if child.tag == 'nd':
						#get node reference
						ref = child.attrib['ref']
						#go get the node
# 						xml_node = 
# 						geo = ndb.GeoPt(chi)
# 						node = classes.Node()
			


class OsmHandler(webapp2.RequestHandler):
	def get(self):

		osm = Osm([-71.0442,42.3622,-71.027,42.3697],{'highway':'*'})
		osm.getdata()

app = webapp2.WSGIApplication([('/osm',OsmHandler)])