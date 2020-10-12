\* The_truck_routing_problem_(closed_north_centre) *\
Minimize
routing_cost: 666.666666667 Extra_trucks + 950 Pattern_0 + 950 Pattern_1
 + 950 Pattern_10 + 525 Pattern_11 + 950 Pattern_12 + 950 Pattern_13
 + 1200 Pattern_14 + 950 Pattern_15 + 950 Pattern_16 + 1200 Pattern_17
 + 1200 Pattern_18 + 700 Pattern_19 + 1200 Pattern_2 + 700 Pattern_20
 + 950 Pattern_21 + 700 Pattern_22 + 950 Pattern_23 + 950 Pattern_24
 + 525 Pattern_25 + 700 Pattern_26 + 700 Pattern_27 + 350 Pattern_28
 + 700 Pattern_3 + 1200 Pattern_4 + 700 Pattern_5 + 700 Pattern_6
 + 700 Pattern_7 + 950 Pattern_8 + 700 Pattern_9 + 1500 Wet_Leases
Subject To
Satisfying_demand_for_Noel_Leeming_Albany: Pattern_1 + Pattern_14 = 1
Satisfying_demand_for_Noel_Leeming_Botany: Pattern_13 + Pattern_26 = 1
Satisfying_demand_for_Noel_Leeming_Glenfield_Clearance: Pattern_1 + Pattern_15
 = 1
Satisfying_demand_for_Noel_Leeming_Henderson: Pattern_17 + Pattern_2 = 1
Satisfying_demand_for_Noel_Leeming_Lunn_Avenue: Pattern_20 + Pattern_8 = 1
Satisfying_demand_for_Noel_Leeming_Manukau_Supa_Centre: Pattern_13
 + Pattern_26 = 1
Satisfying_demand_for_Noel_Leeming_Manukau_Westfield: Pattern_13 + Pattern_27
 = 1
Satisfying_demand_for_Noel_Leeming_Massey: Pattern_18 + Pattern_2 = 1
Satisfying_demand_for_Noel_Leeming_New_Lynn: Pattern_17 + Pattern_5 = 1
Satisfying_demand_for_Noel_Leeming_Newmarket: Pattern_20 + Pattern_7 = 1
Satisfying_demand_for_Noel_Leeming_Ormiston: Pattern_12 + Pattern_28 = 1
Satisfying_demand_for_Noel_Leeming_Papakura: Pattern_23 + Pattern_9 = 1
Satisfying_demand_for_Noel_Leeming_Papatoetoe: Pattern_11 + Pattern_25 = 1
Satisfying_demand_for_Noel_Leeming_Penrose_Clearance: Pattern_10 + Pattern_25
 = 1
Satisfying_demand_for_Noel_Leeming_Queen_Street: Pattern_20 + Pattern_8 = 1
Satisfying_demand_for_Noel_Leeming_Royal_Oak: Pattern_21 + Pattern_7 = 1
Satisfying_demand_for_Noel_Leeming_St_Lukes_Mega: Pattern_17 + Pattern_2 = 1
Satisfying_demand_for_Noel_Leeming_St_Lukes_Westfield: Pattern_17 + Pattern_4
 = 1
Satisfying_demand_for_Noel_Leeming_Sylvia_Park: Pattern_11 + Pattern_24 = 1
Satisfying_demand_for_Noel_Leeming_Wairau_Park: Pattern_0 + Pattern_15 = 1
Satisfying_demand_for_The_Warehouse_Airport: Pattern_10 + Pattern_24 = 1
Satisfying_demand_for_The_Warehouse_Albany: Pattern_1 + Pattern_15 = 1
Satisfying_demand_for_The_Warehouse_Atrium: Pattern_21 + Pattern_7 = 1
Satisfying_demand_for_The_Warehouse_Botany_Downs: Pattern_13 + Pattern_27 = 1
Satisfying_demand_for_The_Warehouse_Clendon: Pattern_23 + Pattern_9 = 1
Satisfying_demand_for_The_Warehouse_Glenfield_Mall: Pattern_0 + Pattern_14 = 1
Satisfying_demand_for_The_Warehouse_Lincoln_Road: Pattern_19 + Pattern_2 = 1
Satisfying_demand_for_The_Warehouse_Lunn_Avenue: Pattern_22 + Pattern_8 = 1
Satisfying_demand_for_The_Warehouse_Manukau: Pattern_12 + Pattern_27 = 1
Satisfying_demand_for_The_Warehouse_Milford: Pattern_0 + Pattern_14 = 1
Satisfying_demand_for_The_Warehouse_Mt_Roskill: Pattern_18 + Pattern_3 = 1
Satisfying_demand_for_The_Warehouse_New_Lynn: Pattern_19 + Pattern_4 = 1
Satisfying_demand_for_The_Warehouse_Newmarket: Pattern_21 + Pattern_6 = 1
Satisfying_demand_for_The_Warehouse_Pakuranga: Pattern_12 + Pattern_26 = 1
Satisfying_demand_for_The_Warehouse_Royal_Oak: Pattern_22 + Pattern_6 = 1
Satisfying_demand_for_The_Warehouse_St_Lukes: Pattern_16 + Pattern_5 = 1
Satisfying_demand_for_The_Warehouse_Sylvia_Park: Pattern_10 + Pattern_24 = 1
Satisfying_demand_for_The_Warehouse_Takanini: Pattern_23 + Pattern_9 = 1
Satisfying_demand_for_The_Warehouse_WestCity: Pattern_18 + Pattern_4 = 1
Satisfying_demand_for_The_Warehouse_Westgate: Pattern_16 + Pattern_3 = 1
max_number_of_shifts: - 2 Extra_trucks + Pattern_0 + Pattern_1 + Pattern_10
 + Pattern_11 + Pattern_12 + Pattern_13 + Pattern_14 + Pattern_15 + Pattern_16
 + Pattern_17 + Pattern_18 + Pattern_19 + Pattern_2 + Pattern_20 + Pattern_21
 + Pattern_22 + Pattern_23 + Pattern_24 + Pattern_25 + Pattern_26 + Pattern_27
 + Pattern_28 + Pattern_3 + Pattern_4 + Pattern_5 + Pattern_6 + Pattern_7
 + Pattern_8 + Pattern_9 - Wet_Leases <= 50
Bounds
0 <= Extra_trucks <= 5
0 <= Wet_Leases <= 9999
Generals
Extra_trucks
Wet_Leases
Binaries
Pattern_0
Pattern_1
Pattern_10
Pattern_11
Pattern_12
Pattern_13
Pattern_14
Pattern_15
Pattern_16
Pattern_17
Pattern_18
Pattern_19
Pattern_2
Pattern_20
Pattern_21
Pattern_22
Pattern_23
Pattern_24
Pattern_25
Pattern_26
Pattern_27
Pattern_28
Pattern_3
Pattern_4
Pattern_5
Pattern_6
Pattern_7
Pattern_8
Pattern_9
End
