from functions import *


if __name__ == "__main__":

    #Load in data for warehouse locations and durations
    Locations = pd.read_csv('WarehouseLocations.csv')
    Durations = pd.read_csv('WarehouseDurations.csv')

    #Partition nodes into north & south groups with 3 subgroups in each
    North_part, South_part = partition(Locations)

    #Generate demand estimates for each node 
    demand_data = generate_demand_estimate(Locations)
    #Generate List of routes for partitions

    #Create route storage for linear progam with both distribution centres
    feasible_routes = []
    for part in North_part:
        #Create route from path & add to total set 
        routes = route_gen(Locations,'Distribution Nouth',part,Durations,demand_data)
        feasible_routes.append(routes)
     
    for part in Sorth_part:
        #Create route from path & add to total set 
        routes = route_gen(Locations,'Distribution South',part,Durations,demand_data)
        feasible_routes.append(routes)


    #For scenario of closing Northen distribution centre
    Partitions = North_part.extend(South_part)
    feasible_routes_south = []
    
    for part in Paritions:
        #Create route from path & add to total set 
        routes = route_gen(Locations,'Distribution South',part,Durations,demand_data)
        feasible_routes_south.append(routes)





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





