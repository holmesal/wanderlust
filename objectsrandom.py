'''
Array of dictionaries that describes every object that gets randomly placed onto the map
name = the name of the object
size = the block dimensions of the object [width, height]
'''
def prob_bush(degree):
	return float(0.1)
	
def prob_tree(degree):
	return float(0.03)

def prob_grass(degree):
	return float(0.7)


objects = [
	
	{
		"name"			:	"bush",
		"size"			:	[1,1],
		"blocks"		:	[2],
		"prob"			:	prob_bush
	},
	
	{
		"name"			:	"bigtree",
		"size"			:	[2,2],
		"blocks"		:	[3,4,5,6],
		"prob"			:	prob_tree
	},
	
	{
		"name"			:	"grass",
		"size"			:	[1,1],
		"blocks"		:	[7],
		"prob"			:	prob_grass
	}

]

