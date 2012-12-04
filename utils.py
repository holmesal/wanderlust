from geo import geohash
from google.appengine.ext import ndb
import classes
import itertools
import json
import logging
import math
import random
import sys
import traceback
import webapp2

class BaseHandler(webapp2.RequestHandler):
	def set_plaintext(self):
		self.response.headers['Content-Type'] = 'text/plain'
	def say(self,stuff):
		'''
		For debugging when I am too lazy to type
		'''
		self.response.out.write('\n')
		self.response.out.write(stuff)
		
	def send_fail(self,auto_log=True):
		if auto_log == True:
			log_error()
		status_code = 500
		status_message = 'Internal Server Error'
		response = {}
		self.send_response(status_code, status_message, response)
	def send_success(self,response):
		status_code = 200
		status_message = 'OK'
		self.send_response(status_code, status_message, response)
	def send_response(self,status_code, status_message, response):
		reply = {
				'meta' : {
						'status_code' : status_code,
						'status_message' : status_message
						},
				'response' : response
				}
		self.response.out.write(json.dumps(reply))

class EnvironmentData(object):
	'''
	A class for grabbing environmental data from a GHash
	'''
	def __init__(self,*ghash_strings):
		'''
		Class wraps around a list of ghashes.
		'''
		
		self.ghash_strings = ghash_strings
		self.ghash_keys = self.create_ghash_keys(ghash_strings)
	
	@staticmethod
	def create_ghash_keys(ghash_strings):
		'''
		Converts a list of ghash strings into a list of ghash_keys
		Also assures that ghashes are the correct length and are strings
		@param ghash_strings: list of string ghashes
		@type ghash_strings: list
		
		@return: a list of ghash_keys that correspond to the provided keys
		@rtype: list
		'''
		ghash_key_list = []
		for ghash in ghash_strings:
			assert ghash.__len__() == classes.GHash._precision, ghash.__len__()
			assert type(ghash) == str or type(ghash) == unicode, type(ghash)
			ghash_key_list.append(ndb.Key(classes.GHash,ghash))
		
		return ghash_key_list
	#===========================================================================
	# Fetching data from a GHash
	#===========================================================================
	def fetch_ground_futures(self):
		'''
		@return: everything on the ground layer for each ghash - list of lists
		@rtype: list
		'''
		return self.fetch_futures(classes.Ground)
	def fetch_structure_futures(self):
		'''
		@return: everything on the structure layer for each ghash - list of lists
		@rtype: list
		'''
		return self.fetch_futures(classes.Structure)
	def fetch_futures(self,model_class):
		'''
		
		@param model_class:
		@type model_class:
		'''
		# a list of list of query iterators for grabbing keys. iter cuts time in half vs fetch
		keys_lists = [model_class.query(ancestor=ghash).iter(batch_size=50,keys_only=True) for ghash in self.ghash_keys]
		# a list of lists of Future entities
		future_entities = [ndb.get_multi_async(keys) for keys in keys_lists]
		return future_entities
	def harvest_futures(self,*list_of_list_of_future_lists):
		result = []
		for list_of_future_lists in list_of_list_of_future_lists:
			r = []
			for future_list in list_of_future_lists:
				r.append([fut.get_result() for fut in future_list])
			result.append(r)
		return result
	def fetch_data(self):
		ground_futures = self.fetch_ground_futures()
		structure_futures = self.fetch_structure_futures()
		
		return self.harvest_futures(ground_futures,structure_futures)
		
	#===========================================================================
	# Packaging
	#===========================================================================
	def package_entities(self,entities):
		'''
		Packages a list of entities by calling each ones package function
		@param entities: a list of entities
		@type entities: list
		
		@return: a packaged list of entities
		@rtype: list
		'''
		return [e.package() for e in entities]
	def package_ghashes(self,ground=[],structures=[]):
		'''
		Packages all of the information for the ghashes
		
		@param ground: list of ground entities with same indexes as ghashes
		@type ground: list
		@param structures: list of structure entities with same indexes as ghashes
		@type structures: list
		
		@return: a nested dictionary with all of the ghash info
		@rtype: dict
		'''
		package = {
				'ghashes' : {}
				}
		for idx,ghash in enumerate(self.ghash_strings):
			packaged_ground = self.package_entities(ground[idx])
			packaged_structures = self.package_entities(structures[idx])
			package['ghashes'].update({
						ghash : {
								'ground' : packaged_ground,
								'structures' : packaged_structures
								}
						
						})
		return package
class PopulateEmptySpace(object):
	buffer_space = 2
	feet_between_points = 5
	def __init__(self,ghash_string,shapes,vectors,points):
		self.ghash_string = ghash_string
		self.ghash_key = ndb.Key(classes.GHash,ghash_string)
		
		
		# these are lists of geo_points
		self.points = points
		self.roads = vectors
		self.shapes = shapes
		
		# get bounds for the geohash
		bbox = geohash.bbox(ghash_string)
		
		#=======================================================================
		# Breaks up geohash into a matrix of points
		#=======================================================================
		# calculate width in feet
		lat1 = lat2 = bbox['n']
		lon1 = bbox['w']
		lon2 = bbox['e']
		span_x_feet = distance_between_points(lat1, lon1, lat2, lon2)
		
		# calculate height in feet
		lon1 = lon2 = bbox['w']
		lat1 = bbox['s']
		lat2 = bbox['n']
		span_y_feet = distance_between_points(lat1, lon1, lat2, lon2)
		
		# calculate the number of steps
		num_x_points = int(math.floor(span_x_feet/self.feet_between_points))
		num_y_points = int(math.floor(span_y_feet/self.feet_between_points))
		
		# calculate the width 
		span_x_degrees = math.fabs(bbox['w'] - bbox['e'])
		span_y_degrees = math.fabs(bbox['n']- bbox['s'])
		
		# calculate the step size in degrees
		dx = span_x_degrees/num_x_points
		dy = span_y_degrees/num_y_points
		
		# calculate the actual arrays of coordinates
		x_points = [bbox['w'] + n*dx for n in range(1,num_x_points+1)]
		y_points = [bbox['n'] - n*dy for n in range(1,num_y_points+1)]
		
		#=======================================================================
		# assign vars
		#=======================================================================
		self.span_x_feet = span_x_feet
		self.span_y_feet = span_y_feet
		self.num_x_points = num_x_points
		self.num_y_points = num_y_points
		self.span_x_degrees = span_x_degrees
		self.span_y_degrees = span_y_degrees
		self.dx = dx
		self.dy = dy
		self.x_points = x_points
		self.y_points = y_points
		
	
	@staticmethod
	def extract_points_from_shapes(grounds):
		nodes = [x.nodes.geo_point for x in grounds]
		return nodes
	@staticmethod
	def extract_points_from_structures(structures):
		nodes = [x.geo_point for x in structures]
		return nodes
		
	def pick_object_kind(self,probabilities):
		'''
		Selects an item to place based on a probability mapping in the probabilities dict
		@param probabilities: probability mapping of probability:entity_kind
		@type probabilities: dict
		
		@return: The type of entity to place in the selected space
		@rtype: ndb.polymodel.PolyModel
		'''
		max_val = sum([key for key in probabilities])
		counter = 0.
		rand_num = random.uniform(0,max_val)
		
		for prob,item in probabilities.iteritems():
			counter += prob
			if rand_num <= counter:
				return item
		raise Exception('Object picking did not work.')
	def run(self):
		'''
		
		'''
		matrix = []
		for y in self.y_points:
			col = []
			for x in self.x_points:
				for shape in self.shapes:
					if self.point_inside_polygon(x, y, shape):
						img = '*'
						break
					else:
						img = '.'
				col.append(img)
			matrix.append(col)
		return matrix

	def step(self,xpoints,ypoints):
		'''
		Moves from one point to the next, raster fashion
		'''
	@staticmethod
	def point_inside_polygon(x,y,poly):

		n = len(poly)
		inside = False
		p1x,p1y = poly[0]
		for i in range(n+1):
			p2x,p2y = poly[i % n]
			if y > min(p1y,p2y):
				if y <= max(p1y,p2y):
					if x <= max(p1x,p2x):
						if p1y != p2y:
							xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
						if p1x == p2x or x <= xinters:
							inside = not inside
			p1x,p1y = p2x,p2y
		
		return inside
		
	
	def point_on_vector(self,x,y,vector):
		'''
		Checks if a point, x,y lies ON a vector. Don't know if it works
		'''
		for i in range(len(vector)):
			p1 = None
			p2 = None
			if i == 0:
				p1 = vector[0]
				p2 = vector[1]
			else:
				p1 = vector[i-1]
				p2 = vector[i]
			if p1[1] == p2[1] and x > min(p1[0], p2[0]) and x < max(p1[0],p2[0]):
				return True
		return False
			
			
#######GEO DISTANCES

def distance_between_points(lat1, lon1, lat2, lon2):
	# all args are in degrees
	# WARNING: loss of absolute precision when points are near-antipodal
	Earth_radius_km = 6371.0 #@UnusedVariable
	Earth_radius_mi = 3958.76
	feet_per_mile = 5280
	RADIUS = Earth_radius_mi*feet_per_mile
	def haversine(angle_radians):
		return math.sin(angle_radians / 2.0) ** 2
	
	def inverse_haversine(h):
		return 2 * math.asin(math.sqrt(h)) # radians
	
	lat1 = math.radians(lat1)
	lat2 = math.radians(lat2)
	dlat = lat2 - lat1
	dlon = math.radians(lon2 - lon1)
	h = haversine(dlat) + math.cos(lat1) * math.cos(lat2) * haversine(dlon)
	return RADIUS * inverse_haversine(h)



def log_error(message=''):
	#called by: log_error(*self.request.body)
	exc_type,exc_value,exc_trace = sys.exc_info() #@UnusedVariable
#	logging.error(exc_type)
#	logging.error(exc_value)
	logging.error(traceback.format_exc(exc_trace))
	if message:
		logging.error(message)

def log_dir(obj,props=None):
	#returns a long multiline string of a regular python object in key: prop
	delimeter = "\n\t\t"
	log_str = delimeter
	try:
		if type(props) is list:
#			logging.debug('log some keys')
			#only display certain keys
			key_list = []
			for key in props:
				key_list.append(key)
			key_list.sort()
			for key in key_list:
				log_str += str(key)+": "+str(getattr(obj,key))+delimeter
		else:
#			logging.debug('log all keys')
			#display all keys
			for key in dir(obj):
				log_str += str(key)+": "+str(getattr(obj,key))+delimeter
	except:
		logging.info('There was an error in log_dir')
	finally:
		return log_str
def log_dict(obj,delimeter= "\n\t\t",*props):
	#returns a long multiline string of a regular python object in key: prop
#	delimeter = "\n\t\t"
	log_str = delimeter

	try:
		if props:
			#only display certain keys
			for key in props:
				if type(obj[key]) == dict:
					log_str += str(key)+": "+ log_dict(obj[key],None,delimeter+'\t\t')+delimeter
				else:
					log_str += str(key)+": "+str(obj[key])+delimeter
		else:
			#display all keys
			key_list = []
			for key in obj:
				key_list.append(key)
			key_list.sort()
			for key in key_list:
				if type(obj[key]) == dict:
					log_str += str(key)+": "+ log_dict(obj[key],None,delimeter+'\t\t')+delimeter

				else:
					log_str += str(key)+": "+str(obj[key])+delimeter
	except Exception,e:
		logging.info('There was an error in log_dict %s',e)
	finally:
		return log_str