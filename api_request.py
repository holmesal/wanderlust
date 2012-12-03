import webapp2
import utils

class RequestMapHandler(utils.BaseHandler):
	def get(self):
		ghash_strings = self.request.get('ghashes')

app = webapp2.WSGIApplication([('/api/request/map',)],debug=False)