import classes
import webapp2


class BaseHandler(webapp2.RequestHandler):
	pass

class Populate(object):
	
	def geo_hash(self,roads,buildings,nature):