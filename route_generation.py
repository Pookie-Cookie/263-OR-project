import pandas as pd
import numpy as np
import openrouteservice as ors
import folium

#get path
#print(route['features'][0]['geometry']['coordinates']
#get route distance
#print(route['features'][0]['properties']['summary']['distance'])
#get route duration
#print(route['features'][0]['properties']['summary']['duration'])


#Load in data for warehouse locations and durations
Locations = pd.read_csv('WarehouseLocations.csv')
Durations = pd.read_csv('WarehouseDurations.csv')

coords = Locations[['Long', 'Lat']]
coords = coords.to_numpy().tolist()
print(Locations['Store'][0])
#generate routes
#route = client.directions(coordinates = [coords[0],coords[18]],profile = 'driving-hgv', format = 'geojson', validate = False)


def route_gen(locations,partition,durations,demand_data):
    '''
This function generates a set of feasible routes for a partition of stores(nodes)
------
Inputs

partition: Set
Set of store location names in the partition

locations: array-like
dataframe containing the longitude and latitude values for the stores

durations: array-like
dataframe containing the travel time between two stores

demand_data: dictionary
dictionary matching the store name to the estimated demand for the store
------
Outputs

routes: array-like
List of routes generated from the partition. (Routes are a list of nodes in order of travel)
------
Pesudocode for route generation

Create set of visited & unvisited
       While there are still unvisited nodes in the partition:
           Create a route with starting node at distribution centre:
           While total demand in route <20:
               Select random node in partition
               If adding node's demand does not exceed toal demand of 20:
                   add node into route & add its estimated demand to route
                   move added node from unvisited to visited in partition
           Save route to list of routes
------
    '''
    #Insert client key to OperRouteService
    client = ors.Client(key = '5b3ce3597851110001cf6248847e5e8faea24926a0ae948072d56e5b')

    #Create set of unvisited & visited nodes
    unvisited = partition
    visited = set()

    #Create list of routes
    routes = []

    #Loop until no nodes remain in unvisited set
    while len(unvisited) > 0:
        #Initialize route: set starting point as south distribution centre & total demand to 0
        route = [locations['Store'][0]]
        total_demand = 0

        #Set count for no. nodes popped to 0
        count = 0
        while total_demand < 20:
            #Pop random node from set of unvisited nodes
            node = unvisited.pop()
            node_demand = demand_data[node]

            if total_demand + node_demand <= 20:
                #Adding node does not exceed demand, add node to route & set of visited nodes
                total_demand = total_demand + node_demand
                visited.add(node)
                route.append(node)

                #Reset popped node counter
                count = 0
            else:
                #Adding node back to set of unvisited as adding causes excess demand
                unvisited.add(node)
                count = count + 1
                #When adding any node causes exceeding of truck capacity, break loop & complete route
                if count == len(unvisited):
                    break
        
        #Create route from nodes in list
        route = create_route(route)                        

        #add route to list
        routes.append(route)

    return routes

def create_route(route)
    #This function takes in list of nodes & orders the route to take the shortest distace/time travelled
    #To be completed

    return route




