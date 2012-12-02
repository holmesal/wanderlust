import classes
import webapp2


class BaseHandler(webapp2.RequestHandler):
	def say(self,stuff):
		self.response.out.write(stuff)

class PopulateGHash(object):
	def __init__(self,ghash):
		assert type(ghash) == str, type(ghash)
		assert ghash.__len__() == 6, ghash.__len__()
		self.ghash = ghash
	def create_ghash_entity(self,
						roads=None,
						buildings=None,
						nature=None,
						**kwargs):
		ghash_entity = classes.GHash(id=self.ghash)
		if roads:
			ghash_entity.roads = roads
		if buildings:
			ghash_entity.buildings = buildings
		if nature:
			ghash_entity.nature = nature
		
		if kwargs.get('auto_put',True) == True:
			ghash_entity.put()
		return ghash_entity
	
	def create_nature_object(self):