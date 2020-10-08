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
    routes_North_1 = route_gen(Locations,North_part[0],Durations,demand_data)
    routes_North_2 = route_gen(Locations,North_part[1],Durations,demand_data)
    routes_North_3 = route_gen(Locations,North_part[2],Durations,demand_data)



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





