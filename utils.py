import classes
import webapp2
from google.appengine.ext import ndb
import logging
import sys
import traceback

class BaseHandler(webapp2.RequestHandler):
	def set_plaintext(self):
		self.response.headers['Content-Type'] = 'text/plain'
	def say(self,stuff):
		self.response.out.write(stuff)

class FetchData(object):
	def __init__(self,ghash_keys):
		'''
		'''
		# create a list of ghash_keys from the ghash
		self.ghash_keys = ghash_keys
	
	@staticmethod
	def create_ghash_keys(ghash_list):
		'''
		Converts a list of ghash strings into a list of ghash_keys
		Also assures that ghashes are the correct length and are strings
		@param ghash_list: list of string ghashes
		@type ghash_list: list
		
		@return: a list of ghash_keys that correspond to the provided keys
		@rtype: list
		'''
		ghash_key_list = []
		for ghash in ghash_list:
			assert ghash.__len__() == classes.GHash._precision, ghash.__len__()
			assert type(ghash) == str, type(ghash)
			ghash_key_list.append(ndb.Key(classes.GHash,ghash))
		
		return ghash_key_list
	def fetch_ground(self):
		'''
		@return: everything on the ground layer for each ghash - list of lists
		@rtype: list
		'''
		ground_lists = []
		for ghash in self.ghash_keys:
			ground_lists.append(classes.Ground.query(ancestor=ghash).fetch(None))
		return ground_lists
	def fetch_buildings(self):
		'''
		Fetches everything on the buildings layer
		@return: everything on the buildings layer for each ghash - list of lists
		@rtype: list
		'''
		building_lists = []
		for ghash in self.ghash_keys:
			building_lists.append(classes.Nature.query(ancestor=ghash).fetch(None))
		return building_lists
	
	def package_ground(self,ground_lists):
		
		

def log_error(message=''):
	#called by: log_error(*self.request.body)
	exc_type,exc_value,exc_trace = sys.exc_info()
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
def log_dict(obj,props=None,delimeter= "\n\t\t"):
	#returns a long multiline string of a regular python object in key: prop
#	delimeter = "\n\t\t"
	log_str = delimeter

	try:
		if type(props) is list:
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