import pandas as pd
import numpy as np
#import openrouteservice as ors
#import folium
import random
from copy import deepcopy
import math

def partition(Locations):
    #Script that outputs lists of stores names after partitions are made across distribution centres

    #records long and lat values of nodes
    coords = Locations[['Long', 'Lat']]
    coords = coords.to_numpy().tolist()

    #computes long and lat values of distribution centres
    Southcoords = coords[0]
    Northcoords = coords[1]

    #creates coords of a position exactly between distribution centres and gradient of a perpendicular lines to divide nodes
    Centrecoords = [(Southcoords[0]+Northcoords[0])/2,(Northcoords[1]+Southcoords[1])/2]
    m = 1/((Northcoords[1]-Southcoords[1])/(Southcoords[0]-Northcoords[0]))

    #create 3 empty sets for partitions of each distribution centre
    N1=[]
    N2=[]
    N3=[]
    S1=[]
    S2=[]
    S3=[]
    #create set for sets
    North=[N1,N2,N3]
    South=[S1,S2,S3]

    #iterate over all locations
    for i in range(len(Locations)):
        if Locations['Type'][i] == 'Distribution':
            #ignore distribution centres
            pass
        elif Centrecoords[1] - Locations['Lat'][i] < m*(Centrecoords[0] - Locations['Long'][i]):
            #divide northern nodes
            if Locations['Lat'][i] > Northcoords[1]:
                N1.append(Locations['Store'][i])
            elif Locations['Long'][i] < Northcoords[0]:
                N2.append(Locations['Store'][i])
            elif Locations['Long'][i] > Northcoords[0]:
                N3.append(Locations['Store'][i])
        else:
            #divide southern nodes
            if Locations['Lat'][i] < Southcoords[1]:
                S1.append(Locations['Store'][i])
            elif Locations['Long'][i] < Southcoords[0]:
                S2.append(Locations['Store'][i])
            elif Locations['Long'][i] > Southcoords[0]:
                S3.append(Locations['Store'][i])
    
    return North,South



def duration_calc(route,duration,route_index,demand_data,scale=None,shift=None):
    """
    This function calculate the duration of a particular route, including the trip back to the starting point and unloading time

    Inputs:

    route: array-like
    List containing the names of the nodes

    durations: array-like
    2D array containing travel time in seconds between nodes

    route_index: array like
    a pd.Series array giving corresponding index values for store names
    ------
    total_duration: int
    duration in seconds of a given route
    """
    
    #initialises duration at 0
    driving_duration = 0
    pallet_duration = 0

    #adds value of arc to duration and 10 mins per pallet
    for i in range(len(route)-1):
        driving_duration += duration[route[i]][route_index[route[i+1]]]
        pallet_duration += 600*demand_data[route[i+1]]

    #accounts for return to distribution centre
    driving_duration += duration[route[-1]][route_index[route[0]]]
    #accounts for unloading at store
    
    #Adds scaling factor for shift
    if scale == True:
        hours = (driving_duration+pallet_duration)/3600
        if shift == True:
            #For routes starting at 8am, we will experience a 20% increase in traffic at 8am and a 25% decrease at 2pm, points between vary linearly
            driving_duration = driving_duration * (1+(0.2*hours - hours**2/30))
        if shift == False:
            #For routes starting at 2am, we will experience a 20% decrease in traffic at 2pm and a 25% increase at 8pm, points between vary linearly
            driving_duration = driving_duration * (1+(hours**2/30 - 0.2*hours))

    total_duration = driving_duration + pallet_duration

    return total_duration
    

def cheapest_insertion(route,durations,route_index,demand_data):
    '''
    This function takes in list of node names & orders the route to take the shortest
    distace/time travelled.
    ------
    Inputs:

    route: array-like
    List containing the names of the nodes

    durations: array-like
    2D array containing travel time in seconds between nodes

    route_index: array like
    a pd.Series array giving corresponding index values for store names

    demand_data: dictionary
    dictionary matching the store name to the estimated demand for the store
    ------
    Returns:
    route: Arraylike:
    List containing an array of ordered nodes by cheapest insertion

    total_duration: int
    duration in seconds of the cheapest route via insertion sort
    '''

    #creates empty list for cheapest route
    cheapest_route = []

    #creates unvisted set
    unvisited = route.copy()

    #removes distibution centre from set and inserts to start of cheapest route
    node = unvisited.pop(0)
    cheapest_route.insert(0,node)

    #while there are still unvisited nodes
    while unvisited != []:
        #creates temp route from current cheapest
        current_route = cheapest_route.copy()
        #presets duration to inf
        duration = float('inf')

        #iterates over unvisited nodes
        for destination in unvisited:
            #iterates over position of inserted node
            for i in range(len(cheapest_route)):
                #inserts node at position
                current_route.insert(i+1,destination)
                #duration calc
                current_duration = duration_calc(current_route,durations,route_index,demand_data)
                if current_duration < duration:
                    #when duration is at min, index and node are recorded
                    node = destination
                    index = i + 1
                #removes node for other iterations
                current_route.remove(destination)
        #inserts node into cheapest route and removes from unlisted
        cheapest_route.insert(index,node)
        unvisited.remove(node)

    #calculates duration of route
    total_duration = duration_calc(cheapest_route,durations,route_index,demand_data)
    #inserts distribution centre at end

    route_info = [cheapest_route, total_duration]

    return route_info

def route_gen(locations,distribution_location,partition,durations,demand_data,route_index):
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

route_index: array like
a pd.Series array giving corresponding index values for store names
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
    #client = ors.Client(key = '5b3ce3597851110001cf6248847e5e8faea24926a0ae948072d56e5b')

    #Create set of unvisited & visited nodes
    unvisited = partition
    visited = set()

    #Create list of routes
    routes = []

    #Loop until no nodes remain in unvisited set
    while len(unvisited) > 0:
        #Shuffle unvisited set
        random.shuffle(unvisited)
        #Initialize route: set starting point & total demand to 0
        route = [distribution_location]
        total_demand = 0

        #Set count for no. nodes popped to 0
        count = 0
        while (total_demand < 20) & (len(unvisited) > 0):
            #Pop first node from randomised set of unvisited nodes
            node = unvisited.pop()
            node_demand = demand_data[node]

            #add node to route preemptively to test for durations
            route.append(node)
            route_duration = cheapest_insertion(route,durations,route_index,demand_data)

            if (total_demand + node_demand <= 20) & (route_duration[1] <= 21600):
                #Adding node does not exceed demand, add node to route & set of visited nodes
                total_demand = total_demand + node_demand
                visited.add(node)
                
                #Reset popped node counter
                count = 0
            else:
                #Adding node back to set of unvisited as adding causes excess demand
                route.remove(node)
                unvisited.append(node)
                count = count + 1
                #When adding any node causes exceeding of truck capacity, break loop & complete route
                if count == len(unvisited):
                    break
        
        #Create cheapest insertion route from nodes in list
        route = cheapest_insertion(route,durations,route_index,demand_data)                        

        #add route to list
        routes.append(route)

    return routes

def generate_demand_estimate(Locations,demand):
#This functions assigns a demand value for each store based on exploratory analysis 

    #Combine store & location strings
    data = demand[['Store','Location','Mean_Demand']]
    data = data.to_numpy().tolist()
    for i in range(len(data)):
        data[i][0] = data[i][0] + " " + data[i][1] 
        del data[i][1]

    #Create dictionary matching demands to the respective stores
    demand_estimate = {data[i][0]: data[i][1] for i in range(40)}

    return demand_estimate

def partition_alt(Locations):
    """
    Function that outputs a list of lists of stores names in partitions, made across geographical locations
    ------
    Inputs:

    locations: array-like
    dataframe containing the longitude and latitude values for the stores
    ------
    Outputs:

    partition: Set
    Set of store location names in the partition

    stores: Set
    Set of all store location names
    """

    #records long and lat values of nodes
    coords = Locations[['Long', 'Lat']]
    coords = coords.to_numpy().tolist()

    #computes long and lat values of distribution centres
    Southcoords = coords[0]
    Northcoords = coords[1]

    #creates coords of a position exactly between distribution centres and gradient of a perpendicular lines to divide nodes
    Centrecoords = [(Southcoords[0]+Northcoords[0])/2,(Northcoords[1]+Southcoords[1])/2]
    m = 1/((Northcoords[1]-Southcoords[1])/(Southcoords[0]-Northcoords[0]))

    #create 3 empty sets for partitions of each distribution centre
    N1=[]
    N2=[]
    N3=[]
    S1=[]
    S2=[]
    S3=[]
    #create set main set
    partitions=[N1,S1,N2,S2,N3,S3]
    stores=[]

    #iterate over all locations
    for i in range(len(Locations)):
        if Locations['Type'][i] == 'Distribution':
            #ignore distribution centres
            pass
        elif Centrecoords[1] - Locations['Lat'][i] < m*(Centrecoords[0] - Locations['Long'][i]):
            #divide northern nodes
            stores.append(Locations['Store'][i])
            if Locations['Lat'][i] > Northcoords[1]:
                N1.append(Locations['Store'][i])
            elif Locations['Long'][i] < Northcoords[0]:
                N2.append(Locations['Store'][i])
            elif Locations['Long'][i] > Northcoords[0]:
                N3.append(Locations['Store'][i])
        else:
            #divide southern nodes
            stores.append(Locations['Store'][i])
            if Locations['Lat'][i] < Southcoords[1]:
                S1.append(Locations['Store'][i])
            elif Locations['Long'][i] < Southcoords[0]:
                S2.append(Locations['Store'][i])
            elif Locations['Long'][i] > Southcoords[0]:
                S3.append(Locations['Store'][i])
    
    return partitions,stores

def route_gen_single(distribution_location,partition,stores,durations,demand_data,route_index):
    '''
This function generates a set of feasible routes for a partition of stores(nodes)
------
Inputs

partition: Set
Set of store location names in the partition

stores: Set
Set of all store location names

locations: array-like
dataframe containing the longitude and latitude values for the stores

distribution_location: string
Name of distribution centre used as origin of route

durations: array-like
dataframe containing the travel time between two stores

demand_data: dictionary
dictionary matching the store name to the estimated demand for the store

route_index: array like
a pd.Series array giving corresponding index values for store names
------
Outputs

routes: array-like
List of routes generated from the partition. (Routes are a list of nodes in order of travel)
------
    '''
    #Insert client key to OperRouteService
    #client = ors.Client(key = '5b3ce3597851110001cf6248847e5e8faea24926a0ae948072d56e5b')

    #Shuffle unvisited set
    random.shuffle(partition)
    #Initialize route: set starting point & total demand to 0
    route = [distribution_location]
    total_demand = 0

    #Set count for no. nodes popped to 0
    count = 0
    while (total_demand < 20) & (len(partition) > 0):
        #Pop first node from randomised set of unvisited nodes
        node = partition.pop()
        node_demand = demand_data[node]

        #add node to route preemptively to test for durations
        route.append(node)
        route_duration = cheapest_insertion(route,durations,route_index,demand_data)

        if (total_demand + node_demand <= 20) & (route_duration[1] <= 14400):
            #Adding node does not exceed demand, add node to route & set of visited nodes
            total_demand = total_demand + node_demand
            stores.remove(node)
            #Reset popped node counter
            count = 0
        elif (len(route) == 2) & (len(partition) == 0):
            stores.remove(node)
            break
        else:
            #Adding node back to set of unvisited as adding causes excess demand
            route.remove(node)
            partition.append(node)
            count = count + 1
            #When adding any node causes exceeding of truck capacity, break loop & complete route
            if count == len(partition):
                break
        
    #Create cheapest insertion route from nodes in list
    route = cheapest_insertion(route,durations,route_index,demand_data)                        

    return route

def demand_calc(route,demand_data,simulate = None):

    """
    This function generates a set of feasible routes for a partition of stores(nodes)
    ------
    Inputs

    route: Set
    Set of store location names visited in the route

    demand_data: dictionary
    dictionary matching the store name to the estimated demand for the store

    ------
    Outputs

    demand: int
    Number of pallets required to fulfill the input route
    """
    #sets base demand to 0
    demand = 0
    for store in route:
        #iterates over all non distribution nodes in route
        if (store != 'Distribution North') & (store != 'Distribution South'):
            #sums demands

            #For simulation, use estimated store demand & std(rn set to 2)
            if simulate:
                simu_demand = round(np.random.normal(demand_data[store],2))
                demand += simu_demand
            else: 
                demand += demand_data[store]
    
    return demand


def route_replicate(routes,distribution,durations,demand_data,route_index):

    #creates empty sets for routes and unvisited stores
    simulate_routes = []
    unvisited = []

    #iterates over our initially planed routes
    for path in routes:
        #creates copy to manipulate
        route = deepcopy(path)

        #creates empty set for current route
        simulate_route = []
        
        for store in path:
            #adds store to replica path
            simulate_route.append(store)

            #tests for demand and duration
            demand = demand_calc(simulate_route,demand_data,simulate = False)
            if (store != 'Distribution North') & (store != 'Distribution South'):
                duration = duration_calc(simulate_route,durations,route_index,demand_data,scale=False,shift=False)
            if (store == 'Distribution North') | (store == 'Distribution South'):
                duration = 0

            if (demand > 20) | (duration > 14400):
                #if demand or duration exceeds normal levels, removes store from path
                simulate_route.remove(store)
            else:
                #else removes from route
                route.remove(store)

        if len(simulate_route) != 1:
            #appends route
            simulate_routes.append(simulate_route)

        if route != []:
            #while there are unvisited stores in route, adds stores to unvisited set
            for store in route:
                if (store != 'Distribution North') & (store != 'Distribution South'):
                    unvisited.append(store)
                route.remove(store)

    while unvisited != []:  
        #creates copy of unvisited to manipulate      
        routeset=deepcopy(unvisited)
        #gens single route from list of unvisited
        single_route=route_gen_single(distribution,unvisited,routeset,durations,demand_data,route_index)
        single_route[0].insert(len(single_route[0]),distribution)
        #appends route
        simulate_routes.append(single_route[0])
    
    #initialise duration 
    route_duration = np.zeros(len(simulate_routes))

    for i in range(len(simulate_routes)):
        if i < 25:
            #calcs duration for 2pm shift
            route_duration[i]=duration_calc(simulate_routes[i][:-1],durations,route_index,demand_data,scale=True,shift=False)
        else:
            #calcs duration for 8am shift
            route_duration[i]=duration_calc(simulate_routes[i][:-1],durations,route_index,demand_data,scale=True,shift=True)

    return simulate_routes, route_duration

def calculate_cost(duration):
    if duration > 14400:
        costs = 175*4
        costs += math.ceil((duration-14400)/3600)*250
    else:
        costs = math.ceil(duration/3600)*175

    return costs
