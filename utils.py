import classes
import webapp2
from google.appengine.ext import ndb
import logging
import sys
import traceback
import json

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

class GHashData(object):
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
			assert type(ghash) == str, type(ghash)
			ghash_key_list.append(ndb.Key(classes.GHash,ghash))
		
		return ghash_key_list
	#===========================================================================
	# Fetching data from a GHash
	#===========================================================================
	def fetch_ground(self):
		'''
		Fetches everything on the ground layer. Convenience wrapper
		@return: everything on the ground layer for each ghash - list of lists
		@rtype: list
		'''
		return self.fetch(classes.Ground)
	def fetch_structures(self):
		'''
		Fetches everything on the structure layer. Convenience wrapper
		@return: everything on the structure layer for each ghash - list of lists
		@rtype: list
		'''
		return self.fetch(classes.Structure)
	def fetch(self,model_class):
		'''
		General function for fetching everything of a certain kind from ghashes
		@param model_class: The model kind of which you desire, e.g. classes.Structure
		@type model_class: ndb.polymodel.Polymodel
		
		@return: a list of lists of stuff in each ghash. sub lists correspond to the parent ghash
		@rtype: list
		'''
		
		return [model_class.query(ancestor=ghash).fetch(None) for ghash in self.ghash_keys]
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