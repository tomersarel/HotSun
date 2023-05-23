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




# rate_set = [1400,1450,1500,1550,1600]
# arr_r = []
# for i in rate_set:
#     manager = Manager(demand_hourly, [period_strategy.PeriodStrategy(10000, 100) for i in range(33)], [],
#                       solar_rad_hourly,
#                       hourly_strategy.GreedyDailyStrategy(), ConfigGetter)
#     batteryChange = ConfigGetter["battery"]
#     batteryChange["charge_rate"] = i
#     arr_r.append(manager.run_simulator(a))
#     print(arr_r[-1])
# result = arr_r[0].copy(deep=True)
#
# array_3d_r = np.stack([df.to_numpy() for df in arr_r])
#
# min_values = np.min(array_3d_r, axis=0)
# max_values = np.max(array_3d_r, axis=0)
# min_df_r = pd.DataFrame(min_values, columns=arr_r[0].columns)
# max_df_r = pd.DataFrame(max_values, columns=arr_r[0].columns)
# min_df_r.to_csv('charge_rate_min_r.csv')
# max_df_r.to_csv('charge_rate_max_r.csv')



'''capacity_set = [4900,4950,5000,5050,5100]
arr_c = []
for i in capacity_set:
    batteryChange = ConfigGetter["battery"]
    batteryChange["capacity"] = i
    arr_c.append(manager.run_simulator(a))

array_3d = np.stack([df.to_numpy() for df in arr_c])

min_values_c = np.min(array_3d, axis=0)
max_values_c = np.max(array_3d, axis=0)
min_df_c = pd.DataFrame(min_values, columns=arr_c[0].columns)
max_df_c = pd.DataFrame(max_values, columns=arr_c[0].columns)
min_df_c.to_csv('charge_rate_min_c.csv')
max_df_c.to_csv('charge_rate_max_c.csv')
'''
d = pd.read_csv("Sumenergy.csv")


def calaParameterError(name, prercent, amount):
    name_set = np.linspace(ConfigGetter["battery"][name]*((100 - prercent)/100), ConfigGetter["battery"][name]*((100 + prercent)/100), amount)
    arr = []
    for i in name_set:
        battery_change = ConfigGetter["battery"]
        battery_change[name] = i
        tmp = manager.run_simulator(a)
        tmp.drop('Date', axis='columns', inplace=True)
        arr.append(tmp)

    simulation_arr = np.stack([df.to_numpy() for df in arr])

    # date_columns = simulation_arr[1]['Date']

    minimum_values = np.min(simulation_arr, axis=0)
    maximum_values = np.max(simulation_arr, axis=0)
    minimum_df = pd.DataFrame(minimum_values, columns=arr[0].columns)
    maximum_df = pd.DataFrame(maximum_values, columns=arr[0].columns)
    # maximum_values.delete('Date', axis='columns', inplace=True)
    # np.delete(maximum_values, 'Date', axis=None)
    # minimum_values.delete('Date', axis='columns', inplace=True)
    # np.delete(minimum_values, 'Date', axis=None)

    total_precent = (maximum_values - minimum_values) * np.reciprocal(d.to_numpy(), where=d.to_numpy() != 0) * 100
    up_precent = (maximum_values - d) * np.reciprocal(d.to_numpy(), where=d.to_numpy() != 0) * 100
    down_precent = (d - minimum_values) * np.reciprocal(d.to_numpy(), where=d.to_numpy() != 0) * 100
    frames = [total_precent, up_precent, down_precent]
    final_precent = pd.concat(frames)
    # maximum_values['Date'] = date_columns
    # minimum_values['Date'] = date_columns
    # final_precent['Date'] = date_columns
    return maximum_df, minimum_df, final_precent

a, b, c = calaParameterError("capacity", 5, 5)
a.to_csv('maximum_capacity.csv')
b.to_csv('minimum_capacity.csv')
c.to_csv('totalprecent_capacity.csv')


a, b, c = calaParameterError("lifetime", 5, 5)
a.to_csv('maximum_lifetime.csv')
b.to_csv('minimum_lifetime.csv')
c.to_csv('totalprecent_lifetime.csv')

a, b, c = calaParameterError("charge_rate", 5, 5)
a.to_csv('maximum_charge_rate.csv')
b.to_csv('minimum_charge_rate.csv')
c.to_csv('totalprecent_charge_rate.csv')

a, b, c = calaParameterError("efficiency", 5, 5)
a.to_csv('maximum_efficiency.csv')
b.to_csv('minimum_efficiency.csv')
c.to_csv('totalprecent_efficiency.csv')

a, b, c = calaParameterError("decay_rate", 5, 5)
a.to_csv('maximum_decay_rate.csv')
b.to_csv('minimum_decay_rate.csv')
c.to_csv('totalprecent_decay_rate.csv')

