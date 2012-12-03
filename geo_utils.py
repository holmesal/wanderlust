from math import sin, cos, asin, degrees, radians, floor, sqrt

#######GEO DISTANCES
Earth_radius_m = 6371000
Earth_radius_mi = 3958.76
RADIUS = Earth_radius_m

def haversine(angle_radians):
	return sin(angle_radians / 2.0) ** 2

def inverse_haversine(h):
	return 2 * asin(sqrt(h)) # radians

def distance_between_points(lat1, lon1, lat2, lon2):
	# all args are in degrees
	# WARNING: loss of absolute precision when points are near-antipodal
	lat1 = radians(lat1)
	lat2 = radians(lat2)
	dlat = lat2 - lat1
	dlon = radians(lon2 - lon1)
	h = haversine(dlat) + cos(lat1) * cos(lat2) * haversine(dlon)
	return RADIUS * inverse_haversine(h)