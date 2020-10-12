import pandas as pd
import numpy as np
from functions import*
from pulp import*

#Load in data for warehouse locations and durations
Locations = pd.read_csv('WarehouseLocations.csv')
Durations = pd.read_csv('WarehouseDurations.csv')
Demands = pd.read_csv('dmnd_avgs.csv')

#Get List of node names: 
Node_names = Locations['Store'].to_numpy().tolist()

#Get dictionary of node names to its respective demand
Demand_estimate = generate_demand_estimate(Locations, Demands)

prob = LpProblem('The truck routing problem',LpMinimize)


print()