from functions import *
from copy import deepcopy
from pulp import *

if __name__ == "__main__":

    #Load in data for warehouse locations and durations
    Locations = pd.read_csv('WarehouseLocations.csv')
    Durations = pd.read_csv('WarehouseDurations.csv')
    Demands = pd.read_csv('dmnd_avgs (1).csv')

    #Generate demand estimates for each node 
    demand_data = generate_demand_estimate(Locations,Demands)

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

    #Generate List of routes for partitions
    no_generations = 2 #Change if we need more


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

    '''
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
    '''


    #LP formulation


    #Get List of node names: 
    Node_names = Locations['Store'][2:].to_numpy().tolist()

    #Get dictionary of node names to its respective demand  
    Node_demands = generate_demand_estimate(Locations, Demands)

    #Create pattern names
    Pattern_names = []
    Patterns = []
    Pattern_costs = []

    #Assigning numerical names to each of the routes
    for i in range(len(feasible_routes)):
        Pattern_names.append(str(i))

    #Separate the routes & respective costs from the feasible_route data format
    for route in feasible_routes:   
        Patterns.append(route[0])
        costs = 0
        #calculate the costs of the routes
        if route[1] > 14400:
            costs = 174*4
            costs += (route[1]-14400)%3600*250
        else:
            costs = route[1]%3600*175

        Pattern_costs.append(costs)

    #Transform route patterns into format usable by linear program
    for i in range(len(Patterns)):
        #List of 40 binarys representing if a store has been visited matching the order of store names.
        new_format = np.zeros((40,), dtype=int)
        for j in range(len(Node_names)):
            #If route contains store, set visited to one
            if Node_names[j] in Patterns[i]:
                new_format[j] = 1
        Patterns[i] = new_format


    #Make dictionary of the routes, the route name & store names
    Patterns = makeDict([Pattern_names,Node_names], Patterns, 0)

    #Make dictionary of routes to their respective costs
    Pattern_costs = {Pattern_names[i]:Pattern_costs[i] for i in range(len(Pattern_names))}

    #Create binary problem variables
    vars = LpVariable.dicts("Pattern", Pattern_names, 0, 1, LpInteger)


    #Create problem variable
    prob = LpProblem('The truck routing problem',LpMinimize)

    #Objective function: minimising chosen routes x cost of each chosen route
    prob += lpSum(vars[i] * Pattern_costs[i] for i in Pattern_names), "routing cost"

    #demand minimum constraint
    for node in Node_names:
        #Selected route must pass through all nodes
        prob += lpSum([vars[j] * Patterns[j][node] for j in Pattern_names]) == 1, "Satisfying demand for " + node

    
    prob.writeLP("TruckRoutingProblem.lp")
    
    prob.solve()
    
    print("Status:", LpStatus[prob.status])
    
    for v in prob.variables():
        print(v.name, "=", v.varValue)

    print("Routing Costs = ", value(prob.objective))
    

    

