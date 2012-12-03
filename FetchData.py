# class for fetching information from the database
import classes
from google.appengine.ext import ndb
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
	
	def fetch_roads(self,ghash_keys):
		for ghash in ghash_keys:
			roads = classes.Road.query(ancestor=ghash).fetch(None)
		return roads
	def fetch_buildings(self,ghash_keys):
		for ghash in ghash_keys:
			buildings = classes.Building.query(ancestor=ghash).fetch(None)
		return buildings
	def fetch_nature(self,ghash_keys):
		for ghash in ghash_keys:
			nature = classes.Nature.query(ancestor=ghash).fetch(None)
		return nature
	def package_roads(self,roads):
		pass
		