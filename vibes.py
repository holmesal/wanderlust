# import structures
import logging
import structures

def calculate_vibe(ground_counts,places_counts):
	'''
	Figure out what degree of urbanity a place is, based on what sort of ground and place layers are returned
	'''
 	logging.info(ground_counts)
 	logging.info(places_counts)
	
	#for now, keep it linear: 0=countryside, 1=city
	#for now, base purely on the number of google places results returned
	
	degree = 0.0001 + float(places_counts["places_count"])/60
	logging.info(degree)
	
	return build_probabilities(degree)
	
def build_probabilities(degree):
	'''
	For each structure, define a relationship to the degree of urbanity
	This will directly influence how many of these structure appear on the map
	'''
	
	probabilities = {
		1 - degree		:	structures.Tree,
		0.1 * degree	:	structures.Dungeon,
		degree			:	structures.Grass
	}
# 	logging.info(probabilities)
	
	#normalize
	total = sum(probabilities.keys())
	# logging.info(total)
	
	normalized_probabilities = {}
	
	for key, value in probabilities.iteritems():
		normalized_probabilities.update({key * (1/total) : value})
	
	logging.info(normalized_probabilities)
	
	return normalized_probabilities