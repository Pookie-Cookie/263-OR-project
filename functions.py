import pandas as pd
import numpy as np
import openrouteservice as ors
import folium

def partition(Locations):
    #Script that outputs lists of stores names after partitions are made across distribution centres

    coords = Locations[['Long', 'Lat']]
    coords = coords.to_numpy().tolist()
    #print(Locations['Store'][0])
    Southcoords = coords[0]
    Northcoords = coords[1]
    Centrecoords = [(Southcoords[0]+Northcoords[0])/2,(Northcoords[1]+Southcoords[1])/2]
    m = 1/((Northcoords[1]-Southcoords[1])/(Southcoords[0]-Northcoords[0]))

    #print(Centrecoords)
    #print(m)

    N1=[]
    N2=[]
    N3=[]
    S1=[]
    S2=[]
    S3=[]
    North=[N1,N2,N3]
    South=[S1,S2,S3]

    for i in range(len(Locations)):
        if Locations['Type'][i] == 'Distribution':
            pass
            #print(Locations['Store'][i])
        elif Centrecoords[1] - Locations['Lat'][i] < m*(Centrecoords[0] - Locations['Long'][i]):
            if Locations['Lat'][i] > Northcoords[1]:
                N1.append(Locations['Store'][i])
            elif Locations['Long'][i] < Northcoords[0]:
                N2.append(Locations['Store'][i])
            elif Locations['Long'][i] > Northcoords[0]:
                N3.append(Locations['Store'][i])
        else:
            if Locations['Lat'][i] < Southcoords[1]:
                S1.append(Locations['Store'][i])
            elif Locations['Long'][i] < Southcoords[0]:
                S2.append(Locations['Store'][i])
            elif Locations['Long'][i] > Southcoords[0]:
                S3.append(Locations['Store'][i])
    """
    for partitions in North:
        print(len(partitions))
    for partitions in South:
        print(len(partitions))
    print(North)
    print(South)
    """
    return North,South

def cheapest_insertion(route):
    '''
    This function takes in list of node names & orders the route to take the shortest
    distace/time travelled.
    ------
    Inputs:

    route: array-like
    List containing the names of the nodes
    ------
    Returns:
    route: Arraylike:
    List containing an array of ordered nodes by cheapest insertion, the total time taken
    in the route

    '''
    return route

def route_gen(locations,distribution_location,partition,durations,demand_data):
    '''
This function generates a set of feasible routes for a partition of stores(nodes)
------
Inputs

partition: Set
Set of store location names in the partition

locations: array-like
dataframe containing the longitude and latitude values for the stores

distribution_location: string
Name of distribution centre used as origin of route

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
        #Initialize route: set starting point & total demand to 0
        route = [distribution_location]
        total_demand = 0

        #Set count for no. nodes popped to 0
        count = 0
        while (total_demand < 20) & (len(unvisited) > 0):
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
                unvisited.append(node)
                count = count + 1
                #When adding any node causes exceeding of truck capacity, break loop & complete route
                if count == len(unvisited):
                    break
        
        #Create cheapest insertion route from nodes in list
        #route = cheapest_insertion(route)                        

        #add route to list
        routes.append(route)

    return routes

def generate_demand_estimate(Locations):
#This functions assigns a demand value for each store based on exploratory analysis 
#To be adjusted in future

    Location_names = Locations.Store.tolist()
    demands = []
    for name in Location_names:
        if "The Warehouse" in name:
            #Estimate average demand for warehouse = 4
            demands.append(4)
        else:
            #Estimate average demand for Noel leeming = 6
            demands.append(6)

    #Create dictionary matching demands to the respective stores
    demand_estimate = {Location_names[i]: demands[i] for i in range(len(demands))}

    return demand_estimate