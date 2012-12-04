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

	
	
	