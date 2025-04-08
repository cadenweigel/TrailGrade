# built in libraries
import json
import math
import os

# third-party libraries
import geojson
import geopandas as gpd
import folium
from trail import *


def print_elevation_data(my_trail):
    increase, decrease = my_trail.get_elevation_up_down()
    print(f"Total Elevation Increase: {increase}  Total Elevation Decrease: {decrease}")
    print(f"Elevation Variance: {my_trail.get_elevation_variance()}")
    print(f"Overall Elevation Change: {my_trail.get_elevation_change()}")


def main():

    # my_trail = Trail("trail_files/Spencer Butte Trail.geojson") #initialize a Trail object with a geojson file
    my_trail = Trail(
        "trail_files/Pre's Trail.geojson"
    )  # initialize a Trail object with a geojson file

    print(my_trail)
    my_trail.get_trail_as_map()  # get trail as an html webpage

    print_elevation_data(my_trail)


if __name__ == "__main__":
    main()
