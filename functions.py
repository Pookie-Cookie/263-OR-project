import pandas as pd
import numpy as np

def partition():
    #Script that outputs lists of stores names after partitions are made across distribution centres

    Locations = pd.read_csv('WarehouseLocations.csv')

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
