"""
haversine.py

Function for calculating the Haversine distance between two points.
"""
from math import sqrt, sin, cos, radians, atan2


def distance(latitude_1, longitude_1, latitude_2, longitude_2):
    """
    Haversine distance formula from https://www.movable-type.co.uk/scripts/latlong.html
    """
    # R is approximately earth's radius (km)
    radius = 6371.0
    latitude_1 = radians(latitude_1)
    latitude_2 = radians(latitude_2)
    longitude_1 = radians(longitude_1)
    longitude_2 = radians(longitude_2)

    delta_latitude = (latitude_2 - latitude_1)
    delta_longitude = (longitude_2 - longitude_1)

    a = sin(delta_latitude / 2)**2 +\
        cos(latitude_1) * cos(latitude_2) *\
        sin(delta_longitude / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    dist = radius * c
    return dist
