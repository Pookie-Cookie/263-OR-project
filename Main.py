from functions import *
from copy import deepcopy
from pulp import *
import math

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

    #Generate List of routes for partitions
    no_generations = 2 #Change if we need more

    
    #Partition nodes into north & south groups with 3 subgroups in each
    North_part_main, South_part_main = partition(Locations)
    Partitions = North_part_main.copy()
    Partitions.extend(South_part_main)

    #Create route storage for linear progam with both distribution centres
    feasible_routes = [[],[]] #[0] = both centres [1] = closed north centre


    for i in range(no_generations): 
        #Deepcopy by value as parition nodes are popped during each cycle
        North_part = deepcopy(North_part_main)
        South_part = deepcopy(South_part_main)

        for part in North_part:
            #Create route from path & add to total set 
            routes = route_gen(Locations,'Distribution North',part,Durations,demand_data,route_index)
            for route in routes:
                feasible_routes[0].append(route)
     
        for part in South_part:
            #Create route from path & add to total set 
            routes = route_gen(Locations,'Distribution South',part,Durations,demand_data,route_index)
            for route in routes:
                feasible_routes[0].append(route)
    

    
    #For scenario of closing Northen distribution centre
    North_part, South_part = partition(Locations)
    Partitions_main = North_part.copy()
    Partitions_main.extend(South_part)
    
    for i in range(no_generations): 
        Partitions = deepcopy(Partitions_main)
        for part in Partitions:
        #Create route from path & add to total set 
            routes = route_gen(Locations,'Distribution South',part,Durations,demand_data,route_index)
            for route in routes:
                feasible_routes[1].append(route)
    

    '''
    #ALTERNATIVE ROUTE GEN - attempts 50 routes < 4 hours before assigning additional stores to trucks then adds wet leased routes
    
    partitions_main,stores_main = partition_alt(Locations)

    distribution = ['Distribution North','Distribution South']

    feasible_routes = []

    for j in range(no_generations):
        partitions=deepcopy(partitions_main) 
        stores=deepcopy(stores_main) 
        N1routes = []
        S1routes = []
        N2routes = []
        S2routes = []
        N3routes = []
        S3routes = []

        routes = [N1routes,S1routes,N2routes,S2routes,N3routes,S3routes]

        count = 0

        #Loop until no store remains unvisited
        while stores != []:
            for i in range(200):
                #Arrangement for all shifts of our avalible 25 trucks: add route to each shift at $175/hr
                if (partitions[i%6] != []) & (count < 50):
                    #Randomise selection of node in partition before generating route
                    random.shuffle(partitions[i%6])
                    route = route_gen_single(Locations,distribution[i%2],partitions[i%6],stores,Durations,demand_data,route_index)
                    routes[i%6].append(route)
                    count += 1
                #Arrangement when all shifts are factored in: attempt to fit stores in existing shifts using additional hours at $250/hr
                elif (partitions[i%6] != []) & (count == 50):
                    for store in partitions:
                        for route in routes[i%6]:
                            route.append(store)

                            route_duration = cheapest_insertion(route,Durations,demand_data,route_index)
                            demand=demand_calc(route,demand_data)
                            if (demand <= 20) & (route_duration[1] <= 21600):
                                stores.remove(store)
                                partitions[i%6].remove(store)
                                break
                            else:
                                route.remove(store)
                    if partitions[i%6] != []:
                        random.shuffle(partitions[i%6])
                        route = route_gen_single(Locations,distribution[i%2],partitions[i%6],stores,Durations,demand_data,route_index)
                        routes[i%6].append(route)

        #Collect all routes into list
        for partition in routes:
            for route in partition:
                feasible_routes.append(route)
    '''

    #LP formulation


    #Get List of node names: 
    Node_names = Locations['Store'][2:].to_numpy().tolist()

    #Get dictionary of node names to its respective demand  
    Node_demands = generate_demand_estimate(Locations, Demands)

    #Separate formulation for the two scenarios
    for i in range (len(feasible_routes)):
        #Create pattern names
        Pattern_names = []
        Patterns = []
        Pattern_costs = []

        #Assigning numerical names to each of the routes
        for j in range(len(feasible_routes[i])):
            Pattern_names.append(str(j))

        #Separate the routes & respective costs from the feasible_route data format
        for route in feasible_routes[i]:   
            Patterns.append(route[0])
            costs = 0
            #calculate the costs of the routes
            if route[1] > 14400:
                costs = 175*4
                costs += math.ceil((route[1]-14400)/3600)*250
            else:
                costs = math.ceil(route[1]/3600)*175

            Pattern_costs.append(costs)

        #Transform route patterns into format usable by linear program
        for j in range(len(Patterns)):
            #List of 40 binarys representing if a store has been visited matching the order of store names.
            new_format = np.zeros((40,), dtype=int)
            for k in range(len(Node_names)):
                #If route contains store, set visited to one
                if Node_names[k] in Patterns[j]:
                    new_format[k] = 1
            Patterns[j] = new_format


        #Make dictionary of the routes, the route name & store names
        Patterns = makeDict([Pattern_names,Node_names], Patterns, 0)

        #Make dictionary of routes to their respective costs
        Pattern_costs = {Pattern_names[j]:Pattern_costs[j] for j in range(len(Pattern_names))}

        #Create binary problem variables
        vars = LpVariable.dicts("Pattern", Pattern_names, 0, 1, LpInteger)
        extra_trucks = LpVariable("Extra trucks", 0, 5, LpInteger)
        wet_leases = LpVariable("Wet Leases", 0, 9999, LpInteger)

        #Create problem variable
        if i == 0:
            prob = LpProblem('The truck routing problem (both distribution centres)',LpMinimize)
        else:
            prob = LpProblem('The truck routing problem (closed north centre)',LpMinimize)
        #Objective function: minimising chosen routes x cost of each chosen route
        prob += lpSum(vars[j] * Pattern_costs[j] for j in Pattern_names) + wet_leases*1500 + extra_trucks*20000/30, "routing cost"

        #demand minimum constraint
        for node in Node_names:
            #Selected route must pass through all nodes
            prob += lpSum([vars[j] * Patterns[j][node] for j in Pattern_names]) == 1, "Satisfying demand for " + node

        num_shifts = 50 

        prob += lpSum(vars) <= num_shifts + extra_trucks*2 + wet_leases, "max number of shifts"

        if i == 0:
            prob.writeLP("TRP_both_centres.lp")
        else:
            prob.writeLP("TRP_south_only.lp")
    
        prob.solve()
    
        #print("Status:", LpStatus[prob.status])
    
        print("Selected route / cost in $")
        count = 0
        for v in prob.variables():
            if v.varValue == 1:
                count = count + 1
                print(v.name, "=", Pattern_costs[v.name[8:]])
        print("Total no. truck shifts = ", count)
        print("Total routing Costs = ", value(prob.objective))
    

    

