import pandas as pd
import numpy as np
import openrouteservice as ors
import folium

#Insert client key to OperRouteService
client = ors.Client(key = '5b3ce3597851110001cf6248847e5e8faea24926a0ae948072d56e5b')

#Load in data for warehouse locations and durations
Locations = pd.read_csv('WarehouseLocations.csv')
Durations = pd.read_csv('WarehouseDurations.csv')

coords = Locations[['Long', 'Lat']]
coords = coords.to_numpy().tolist()

#generate routes
route = client.directions(coordinates = [coords[0],coords[18]],profile = 'driving-hgv', format = 'geojson', validate = False)

#Pesudocode for route generation
#1. Create parition for nodes
#2. For each partition of nodes,
#       While there are still unvisited nodes in the partition:
#           Create a route:
#           While total demand in route <20:
#               Select random node in partion
#               If adding node's demand does not exceed toal demand of 20:
#                   add node into route & add its estimated demand to route
#                   move added node from unvisited to visited in partition
#           Save route to list of routes



#get path
#print(route['features'][0]['geometry']['coordinates']
#get route distance
#print(route['features'][0]['properties']['summary']['distance'])
#get route duration
#print(route['features'][0]['properties']['summary']['duration'])

