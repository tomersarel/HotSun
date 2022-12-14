from df_objects import *

"""d = DemandHourlyStateData()
print(d.get_demand_hourly_by_range_of_date(datetime.datetime(2017, 1, 1, 13), datetime.datetime(2017, 1, 3, 13)))
print(d.get_demand_daily_by_date(datetime.datetime(2049, 1, 1, 13)))"""

d = SolarRadiationHourlyMonthData()
print(d.get_solar_rad_daily_by_range_of_date(datetime.datetime(2017, 12, 30, 13), datetime.datetime(2018, 1, 3, 13)))
