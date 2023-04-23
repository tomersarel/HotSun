import math
from distutils.command.config import config
import pandas as pd
import numpy as np

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


#
#
# d['SumOfTheSolar'] = pd.Series([d['Batteries'][hour] + d['Solar'][hour] + d['Buying'][hour]  for hour in d.index])
#
# d.to_csv('Sumenergy.csv')
# print(d)
h = pd.read_csv("data/hourlyConsumptionPrediction.csv")
d = pd.read_csv("Sumenergy.csv")
#לבדוק שהמכירה קטנה מסך האנרגיה שלנו
'''for hour in d.index:
    if d["Selling"][hour] > d["SumOfTheSolar"][hour]:
        print('error')'''

#לבדוק שסך האנרגיה שלנו קטנה ממקום האכסון שלנו
'''for hour in d.index:
    if d["Selling"][hour] > 0 and d["Buying"][hour] > 0:
        print('error')'''

'''for hour in d.index:
    if h[str(hour % 24)][int(hour/24)] < d["SumOfTheSolar"][hour]:
        print(h[str(hour % 24)][int(hour/24)] - d["SumOfTheSolar"][hour])'''

'''for hour in d.index:
    if 22 < hour % 24 or hour % 24 < 4:
        if d["Storaged"][hour] > 0:
            print('error')'''

storage = 0
for hour in d.index:
    storage += d["Storaged"][hour]
    storage -= d["Batteries"][hour]
    if storage < 0:
        print(":(")




# print(len(h.index))
# print(len(d.index))

# i = 0
# a = True
# for hour in d.index:
#     # print (hour)
#     if math.isclose(d['SumOfTheSolar'][hour],h[str(hour % 24)][int(hour/24)],abs_tol=10**-6):
#
#         pass
#     else:
#         print(d['SumOfTheSolar'][hour], h[str(hour % 24)][int(hour/24)])
# print(a)