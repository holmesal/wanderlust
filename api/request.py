import webapp2
import utils
import logging
from datetime import datetime
class RequestMapHandler(utils.BaseHandler):
	def get(self):
		try:
			# for debugging
			times = {}
			t0 = datetime.now()
			ghash_string = self.request.get('ghashes')
			ghash_strings = ghash_string.split(',')
			environment = utils.EnvironmentData(*ghash_strings)
			
			t1 = datetime.now()
			# grab data async
			ground_futures = environment.fetch_ground_futures()
			structure_futures = environment.fetch_structure_futures()
			times.update({'fetch_async' : str(datetime.now() - t1)})
			
			t1 = datetime.now()
			ground,structures = environment.harvest_futures(
														ground_futures,
														structure_futures
														)
			times.update({'harvest' : str(datetime.now() - t1)})
			
			t1 = datetime.now()
			response = environment.package_ghashes(ground, structures)
			times.update({'package' : str(datetime.now() - t1)})
			
			times.update({'total' : str(datetime.now() - t0)})
			response.update({'times' : times})
			self.send_success(response)
		except:
			self.send_fail()

app = webapp2.WSGIApplication([('/api/request/map',RequestMapHandler)],debug=False)