import json
import jinja2
import os
import logging

def visualize(self,center,**kwargs):
	
	'''
	roads are many linestrings
	leisures are a multipolygon
	natures are a multipolygon
	buildingfootprints are a multipolygon
	structures are a multipoint
	'''
	
	def visual_package(input_array,display_type):
	
		output = []
	
		for feature in input_array:
			packaged_feature = {
				"type"		:	"Feature",
				"properties":	{
					"subname"	:	feature["subname"],
					"subtype"	:	feature["subtype"]
				}
			}
			
			if display_type == "LineString":
				packaged_feature["geometry"] = {
					"type"			:	"LineString",
					"coordinates"	:	feature["geometry"]
				}
			elif display_type == "Polygon":
				packaged_feature["geometry"] = {
					"type"			:	"Polygon",
					"coordinates"	:	[feature["geometry"]]
				}
			
			#FIXES ------
			#fix the coastline to display as a LineString
			if feature["subtype"] == "coastline":
				packaged_feature["geometry"] = {
					"type"			:	"LineString",
					"coordinates"	:	feature["geometry"]
				}
			
			output.append(json.dumps(packaged_feature))
			
		return output
	
	roads = visual_package(kwargs.get("roads",[]),"LineString")
	natures = visual_package(kwargs.get("natures",[]),"Polygon")
	leisures = visual_package(kwargs.get("leisures",[]),"Polygon")
	buildingfootprints = visual_package(kwargs.get("buildingfootprints",[]),"Polygon")
	structures = visual_package(kwargs.get("structures",[]),"Polygon")
	
	
	output = {"center":center,"roads":roads,"natures":natures,"leisures":leisures,"buildingfootprints":buildingfootprints}
	
	jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
	template = jinja_environment.get_template('templates/world.html')
	self.response.out.write(template.render(output))


def visualize_blocks(self,matrix,blocks_meta,ul_corner_geo,width,height):
	'''
	Width should be in degrees
	'''

	base_lat = ul_corner_geo[1]
	base_lon = ul_corner_geo[0]
	
	output = {"center":[base_lat,base_lon],"roads":[],"bushes":[],"trees":[],"grass":[]}
	
	for row_idx,row_item in enumerate(matrix):
		for idx,item in enumerate(row_item):
			
			dx = idx*width
			dy = row_idx*height
	
			packaged_feature = {
				"type"		:	"Feature",
				"properties":	{
					"subname"	:	blocks_meta[item]["name"],
					"subtype"	:	item
				},
				"geometry"	:	{
					"type"			:	"Polygon",
					"coordinates"	:	[[
						[base_lon+dx,base_lat-dy],
						[base_lon+dx,base_lat-height-dy],
						[base_lon+width+dx,base_lat-height-dy],
						[base_lon+width+dx,base_lat-dy]
					
					]]
				}
			}
			
			if item == 1:
				output["roads"].append(json.dumps(packaged_feature))
			elif item == 2:
				output["bushes"].append(json.dumps(packaged_feature))
			elif item in [3,4,5,6]:
				output["trees"].append(json.dumps(packaged_feature))
			elif item == 7:
				output["grass"].append(json.dumps(packaged_feature))
			
			
			
# 	output["blocks"] = output["blocks"][0]
	
# 	logging.info(output)
			
	
	
	jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
	template = jinja_environment.get_template('templates/world_blocks.html')
	self.response.out.write(template.render(output))
		