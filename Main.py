from functions import *
from copy import deepcopy


if __name__ == "__main__":

    #Load in data for warehouse locations and durations
    Locations = pd.read_csv('WarehouseLocations.csv')
    Durations = pd.read_csv('WarehouseDurations.csv')

    #create pd.Series for store names so we can access index of stores from store name inputs
    store_index=[]
    for store in Locations['Store']:
        for i in range(len(Locations['Store'])):
            if Locations['Store'][i] == store:
                store_index.append(i)
    route_index = pd.Series(data=store_index, index = Locations['Store'])

    #Partition nodes into north & south groups with 3 subgroups in each
    North_part_main, South_part_main = partition(Locations)
    Partitions = North_part_main.copy()
    Partitions.extend(South_part_main)

    #Generate demand estimates for each node 
    demand_data = generate_demand_estimate(Locations)

    #Generate List of routes for partitions
    no_generations = 100 #Change if we need more


    #Create route storage for linear progam with both distribution centres
    feasible_routes = []
    for i in range(no_generations): 
        #Deepcopy by value as parition nodes are popped during each cycle
        North_part = deepcopy(North_part_main)
        South_part = deepcopy(South_part_main)

        for part in North_part:
            #Create route from path & add to total set 
            routes = route_gen(Locations,'Distribution North',part,Durations,demand_data,route_index)
            for route in routes:
                feasible_routes.append(route)
     
        for part in South_part:
            #Create route from path & add to total set 
            routes = route_gen(Locations,'Distribution South',part,Durations,demand_data,route_index)
            for route in routes:
                feasible_routes.append(route)


    #For scenario of closing Northen distribution centre
    feasible_routes_south = []
    North_part, South_part = partition(Locations)
    Partitions_main = North_part.copy()
    Partitions_main.extend(South_part)
    
    for i in range(no_generations): 
        Partitions = deepcopy(Partitions_main)
        for part in Partitions:
        #Create route from path & add to total set 
            routes = route_gen(Locations,'Distribution South',part,Durations,demand_data,route_index)
            for route in routes:
                feasible_routes_south.append(route)

    print()





    #get path
    #print(route['features'][0]['geometry']['coordinates']
    #get route distance
    #print(route['features'][0]['properties']['summary']['distance'])
    #get route duration
    #print(route['features'][0]['properties']['summary']['duration'])




    #coords = Locations[['Long', 'Lat']] 
    #coords = coords.to_numpy().tolist()
    
    #generate routes
    #route = client.directions(coordinates = [coords[0],coords[18]],profile = 'driving-hgv', format = 'geojson', validate = False)





