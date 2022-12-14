from df_objects import *

d = DemandHourly()
print(d.get_demand_daily_by_range_of_date(datetime.datetime(2017, 1, 1, 13), datetime.datetime(2017, 1, 3, 13)))
