from df_objects import *

d = DemandHourly()
print(d.get_demand_by_date(datetime.datetime(2017, 1, 1, 13)))