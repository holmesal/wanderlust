# import structures
import logging
import structures
import objectsrandom
import random
import utils
from sets import Set
from blocks import blocks

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
	
	probabilities = {}
	
	for idx,item in enumerate(objectsrandom.objects):
		logging.info(item["prob"](degree))
		probabilities.update({item["prob"](degree)	:	idx})
	
	return probabilities
# 	
# 	probabilities = {
# 		1 - degree		:	structures.Tree,
# 		0.1 * degree	:	structures.Dungeon,
# 		degree			:	structures.Grass
# 	}
# # 	logging.info(probabilities)
# 	
# 	#normalize
# 	total = sum(probabilities.keys())
# 	# logging.info(total)
# 	
# 	normalized_probabilities = {}
# 	
# 	for key, value in probabilities.iteritems():
# 		normalized_probabilities.update({key * (1/total) : value})
# 	
# 	logging.info(normalized_probabilities)
# 	
# 	return normalized_probabilities

def pick_object_kind(probabilities):
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

def allclear(matrix,iterrows,itercols):
	#logging.info('Trying to place object in rows '+str(iterrows) + " and cols "+str(itercols))
	
	occupied = False
	
	try:
	
		for iter_row in iterrows:
			for iter_col in itercols:
				if matrix[iter_row][iter_col] != 0:
					occupied = True
		
		if occupied == True:
			#logging.info("Space was occupied")
			return False
		else:
			return True
	
	except Exception,e:
		#logging.info('Hit the edge of the boundary')
# 		utils.log_error(e)
		return False
		

def placeobject(matrix,probs,row_idx,idx,blocks_used):

	to_place = objectsrandom.objects[pick_object_kind(probs)]
	
	#logging.info(row_idx)
	#logging.info(idx)
	delx = to_place["size"][0]
	dely = to_place["size"][1]
	iterrows = range(row_idx,row_idx+dely)
	itercols = range(idx,idx+delx)
	#logging.info(iterrows)
	#logging.info(itercols)
	#logging.info('---')
	
	if allclear(matrix,iterrows,itercols):
		blocks = to_place["blocks"]
		block_idx = 0
		for iter_row in iterrows:
			for iter_col in itercols:
				matrix[iter_row][iter_col] = blocks[block_idx]
				blocks_used.add(blocks[block_idx])
				block_idx += 1
	
	else:
		placeobject(matrix,probs,row_idx,idx,blocks_used)
	
	return matrix,blocks_used
	
def place_vibe_objects(matrix):
	#get probabilities
	probs = build_probabilities(0.5)
	
	#initialize blocks array for output
	blocks_used = set([])
	
	for row_idx,row_item in enumerate(matrix):
		for idx,item in enumerate(row_item):
			if item == 0:
				matrix,blocks_used = placeobject(matrix,probs,row_idx,idx,blocks_used)
	
	blocks_meta = {}
	
	for block in blocks_used:
		blocks_meta.update({block:blocks[block]})
	
	return matrix,blocks_meta