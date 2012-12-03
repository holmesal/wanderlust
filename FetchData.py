# class for fetching information from the database
import classes
class FetchData(object):
	def __init__(self,ghash_list):
		'''
		@param ghash_list: a list of ghash strings (6 precision) we want to grab info from
		@type ghash_list: list
		'''
		
		# quality control!
		for ghash in ghash_list:
			assert ghash.__len__() == classes.GHash._precision, ghash.__len__()
			assert type(ghash) == str, type(ghash)
		self.ghash_list = ghash_list
	
	def fetch_roads(self):
		for ghash in self.ghash_list:
			