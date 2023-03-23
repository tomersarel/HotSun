import math
from distutils.command.config import config
import pandas as pd

import battery
import hourly_strategy
import period_strategy
from df_objects import DemandHourlyCityData, SolarProductionHourlyDataPVGIS, DemandHourlyStateData
from manager import Manager
from config_manager import ConfigGetter


demand_hourly = DemandHourlyStateData()
solar_rad_hourly = SolarProductionHourlyDataPVGIS(ConfigGetter['LOCATION']['longitude'],
                                                          ConfigGetter['LOCATION']['latitude'],
                                                          ConfigGetter['solar']['peakpower'],
                                                          ConfigGetter['solar']['loss'])
manager = Manager(demand_hourly, [period_strategy.PeriodStrategy(10000, 100) for i in range(33)], [],
                      solar_rad_hourly,
                      hourly_strategy.GreedyDailyStrategy(), ConfigGetter)
def a(a):
    pass


# d = manager.run_simulator(a)
#
#
# d['SumOfTheSolar'] = pd.Series([d['Batteries'][hour] + d['Solar'][hour] + d['Buying'][hour]  for hour in d.index])
#
# d.to_csv('Sumenergy.csv')
# print(d)


h = pd.read_csv("data/hourlyConsumptionPrediction.csv")
d = pd.read_csv("Sumenergy.csv")
print(len(h.index))
print(len(d.index))

i = 0
a = True
for hour in d.index:
    # print (hour)
    if math.isclose(d['SumOfTheSolar'][hour],h[str(hour % 24)][int(hour/24)],abs_tol=10**-6):

        pass
    else:
        print(d['SumOfTheSolar'][hour], h[str(hour % 24)][int(hour/24)])
print(a)