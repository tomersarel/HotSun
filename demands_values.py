import pandas as pd
from demands_cal import total_demand_table
days_in_a_month={
    0:31,
    1:28,
    2:31,
    3:30,
    4:31,
    5:30,
    6:31,
    7:31,
    8:30,
    9:31,
    10:30,
    11:31
}
"""
hotel_demand_for_month_factor = [0.08729817612864943, 0.16333987515943435, 0.16494866549625728, 0.1659551050117698, 0.1636580613351361, 0.162013847279344, 0.09278626958940887]
s=sum(hotel_demand_for_month_factor)/(len(hotel_demand_for_month_factor))
L=[i/s for i in hotel_demand_for_month_factor]
print(L)
print(sum(L))"""

"""fd=pd.read_csv("C:\\Users\\user\\Downloads\\maagar_asakim.csv",encoding = "utf_16", sep=';')"""
"""print(fd)"""
"""restaurants=0
sum_of_meters=0
for row in fd.index:
    if(fd["shetach"][row]>0 and fd["k_category"][row] in {3} and fd["k_anaf_rashi_merkaz_lemechkar"][row] in {11}):
        print(fd["k_anaf_rashi_merkaz_lemechkar"][row],fd["t_anaf_rashi_merkaz_lemechkar"][row])
        restaurants = restaurants +1
        sum_of_meters=sum_of_meters+fd["shetach"][row]
print(restaurants)
print(sum_of_meters/restaurants*38*3/4)"""
DT=total_demand_table(468746,1.007,17466,2.21,1.3,102,1.02,1.034,75058,7828,1.034,1.04,4666,2013,1.034,1.04,20000,2740,1.034,1.04,4666,8288,1.034,1.04,4666)
print(DT[2031][3][1][8]/DT[2021][3][1][8])