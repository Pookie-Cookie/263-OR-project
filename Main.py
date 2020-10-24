from functions import *
from copy import deepcopy
from pulp import *
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde



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
    no_generations = 10 #Change if we need more

    
    #Partition nodes into north & south groups with 3 subgroups in each
    North_part_main, South_part_main = partition(Locations)
    Partitions = North_part_main.copy()
    Partitions.extend(South_part_main)

    #Create route storage for linear progam with both distribution centres
    feasible_routes = [[],[]] #[0] = both centres [1] = closed north centre

    
    #ROUTE GEN - attempts 50 routes < 4 hours before assigning additional stores to trucks then adds wet leased routes
    
    partitions_main,stores_main = partition_alt(Locations)

    distribution = ['Distribution North','Distribution South']

    for k in range(2):
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
                        #generates route for both distribution scenario
                        if k == 0:
                            route = route_gen_single(distribution[i%2],partitions[i%6],stores,Durations,demand_data,route_index)
                        #generates route for northern distibution closure scenario
                        else:
                            route = route_gen_single(distribution[1],partitions[i%6],stores,Durations,demand_data,route_index)
                        #adds route to partition routes and increases count
                        routes[i%6].append(route)
                        count += 1
                    #Arrangement when all shifts are factored in: attempt to fit stores in existing shifts using additional hours at $250/hr
                    elif (partitions[i%6] != []) & (count == 50):
                        for store in partitions:
                            for route in routes[i%6]:
                                #for each unvisited stores in partitions, attempts to add store to existing route
                                route.append(store)

                                #tests for demand and duration
                                route_duration = cheapest_insertion(route,Durations,demand_data,route_index)
                                demand=demand_calc(route,demand_data)
                                if (demand <= 20) & (route_duration[1] <= 21600):
                                    #if demand and duration are satisfied, removes store from unvisited sets
                                    stores.remove(store)
                                    partitions[i%6].remove(store)
                                    break
                                else:
                                    #else removes store from route
                                    route.remove(store)
                        #if routes fail to include additional nodes, adds additional routes as per normal
                        if partitions[i%6] != []:
                            random.shuffle(partitions[i%6])
                            if k == 0:
                                route = route_gen_single(distribution[i%2],partitions[i%6],stores,Durations,demand_data,route_index)
                            else:
                                route = route_gen_single(distribution[1],partitions[i%6],stores,Durations,demand_data,route_index)
                            
                            routes[i%6].append(route)

            #Collect all routes into list
            for partition in routes:
                for route in partition:
                    route[0].insert(len(route[0]),route[0][0])
                    feasible_routes[k].append(route)
    

    #LP formulation


    #Get List of node names: 
    Node_names = Locations['Store'][2:].to_numpy().tolist()

    #Get dictionary of node names to its respective demand  
    Node_demands = generate_demand_estimate(Locations, Demands)

    chosenroute = [[],[]]
    total_cost = []

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
            costs = calculate_cost(route[1])
            #calculate the costs of the routes

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

        if i == 0:
            prob += lpSum(vars[j] * Pattern_costs[j] for j in Pattern_names) + wet_leases*1500 + extra_trucks*20000/30, "routing cost"
        else:
            #Converting the $400000 saved by closing the northern distribution centre into savings per day
            prob += lpSum(vars[j] * Pattern_costs[j] for j in Pattern_names) + wet_leases*1500 + extra_trucks*20000/30 - 400000/30, "routing cost"
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
    
        #Saving results to csv file
        if i == 0:
            # Northern and southern distribution
            f = open('routes_statusquo.csv','w')
        else:
            # Southern only
            f = open('routes_closure.csv','w')

        

        print("Selected route / cost in $")
        count = 0
        for v in prob.variables():
            if v.varValue == 1:
                count = count + 1

                print(v.name, "=", Pattern_costs[v.name[8:]])
                route = feasible_routes[i][int(v.name[8:])][0]
                f.write(','.join(route))
                f.write('\n')
                
                chosenroute[i].append(feasible_routes[i][int(v.name[8:])][0])
        print("Total no. truck shifts = ", count)
        print("Total routing Costs = ", value(prob.objective))
        total_cost.append(value(prob.objective))

        f.close()

    demand_random = deepcopy(demand_data)
    Locations = pd.read_csv('WarehouseLocations.csv')
    
    sim_size = 10000

    for x in range (2):
        
        total_cost_simulated = []
        #attempts to replicate chosen routes and ammends shortcomings with extra routes
        for i in range(sim_size):
            for store in Locations['Store']:
                if (store != "Distribution North") & (store != "Distribution South"):
                    #simulates random demand prior to function call
                    demand_random[store] = min(round(np.random.normal(demand_data[store],2)),20)
            route_simulate,route_durations=route_replicate(chosenroute[x],distribution[x],Durations,demand_random,route_index)
            route_costs = []
            for j in range(len(route_durations)):
                route_costs.append(calculate_cost(route_durations[j]))
            if x == 1:
                 total_cost_simulated.append(sum(route_costs) - 400000/30)
            else:
                total_cost_simulated.append(sum(route_costs))

        cost_sort = deepcopy(total_cost_simulated)
        cost_sort.sort()

        cost_density = gaussian_kde(total_cost_simulated)
        xs = np.linspace(cost_sort[0],cost_sort[-1],200)
        cost_density.covariance_factor = lambda : .2
        cost_density._compute_covariance()
        plt.rcParams["figure.figsize"] = (11,8)
        plt.plot(xs,cost_density(xs), label = "Cost Simulation")

        plt.axvline(x = cost_sort[round(sim_size*0.025)], color = 'k', label = ("95% Percentile Interval = [" + '{:.2f}'.format(cost_sort[round(sim_size*0.025)]) + " , " + '{:.2f}'.format(cost_sort[round(sim_size*0.975)]) + "]"))
        plt.axvline(x = cost_sort[round(sim_size*0.975)], color = 'k')
        plt.axvline(x = cost_sort[round(sim_size*0.5)], color = 'g', label = "Median cost (with simulation) = $" + '{:.2f}'.format(cost_sort[round(sim_size*0.5)]))
        plt.axvline(x = total_cost[x], color = 'r', label = ("Optimal Cost (without simulation) = $" + '{:.2f}'.format(total_cost[x])))

        if x == 1:
            plt.title("Cost Simulation of Northern Distribution Closure Delivery Model")
        else:
            plt.title("Cost Simulation of Standard Delivery Model")
        
        plt.xlabel("Cost ($)")
        plt.ylabel("Density")
        plt.legend(loc = 1)
        

        
        if x == 1:
            plt.savefig("NorthernClosureSim.png")
        else:
            plt.savefig("StandardSim.png")
        plt.show()
        print(len(route_simulate))
    

