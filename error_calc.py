import math
import matplotlib.pyplot as plt
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


def n(a):
    pass


'''data = {'a': np.arange(50),
        'c': np.random.randint(0, 50, 50),
        'd': np.random.randn(50)}
data['b'] = data['a'] + 10 * np.random.randn(50)
data['d'] = np.abs(data['d']) * 100

plt.scatter('a', 'b', c='c', s='d', data=data)
plt.xlabel('entry a')
plt.ylabel('entry b')
plt.show()
'''
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
original_df = manager.run_simulator(n)
original_df.drop('Date', axis='columns', inplace=True)
original_df.to_csv('original_data')

def calc_parameter_error(name, prercent, amount):

    name_set = np.linspace(ConfigGetter["battery"][name]*((100 - prercent)/100), ConfigGetter["battery"][name]*((100 + prercent)/100), amount)
    arr = []
    for i in name_set:
        ConfigGetter["battery"][name] = i
        tmp = manager.run_simulator(n)
        tmp.drop('Date', axis='columns', inplace=True)
        np_a = tmp.to_numpy()
        arr.append(np_a)

    simulation_arr = np.stack(arr)

    minimum_values = np.min(simulation_arr, axis=0)
    maximum_values = np.max(simulation_arr, axis=0)

    minimum_df = pd.DataFrame(minimum_values, columns=['Batteries', 'Solar', 'Buying',
                                                       'Selling', 'Lost', 'Storaged',
                                                       'NewBatteries', 'AllBatteries',
                                                       'NewSolarPanels', 'AllSolarPanels'])
    maximum_df = pd.DataFrame(maximum_values, columns=['Batteries', 'Solar', 'Buying',
                                                       'Selling', 'Lost', 'Storaged',
                                                       'NewBatteries', 'AllBatteries',
                                                       'NewSolarPanels', 'AllSolarPanels'])
    np_original = original_df.to_numpy()

    reciprocal_values = np.reciprocal(np_original, where=np_original != 0)

    pd_df_with_nones = pd.DataFrame(reciprocal_values)
    pd_df_with_nones.fillna(0, inplace=True)
    reciprocal_values = pd_df_with_nones.to_numpy()

    total_precent = (maximum_values - minimum_values) * reciprocal_values * 100
    up_precent = (maximum_values - np_original) * reciprocal_values * 100
    down_precent = (np_original - minimum_values) * reciprocal_values * 100

    total_precent = pd.DataFrame(total_precent)
    up_precent = pd.DataFrame(up_precent)
    down_precent = pd.DataFrame(down_precent)


    frames = [total_precent, up_precent, down_precent]

    final_precent = pd.concat(frames)
    return maximum_df, minimum_df, final_precent


a, b, c = calc_parameter_error("capacity", 5, 5)
a.to_csv('maximum_capacity.csv')
b.to_csv('minimum_capacity.csv')
c.to_csv('totalprecent_capacity.csv')


a, b, c = calc_parameter_error("lifetime", 5, 5)
a.to_csv('maximum_lifetime.csv')
b.to_csv('minimum_lifetime.csv')
c.to_csv('totalprecent_lifetime.csv')

a, b, c = calc_parameter_error("charge_rate", 5, 5)
a.to_csv('maximum_charge_rate.csv')
b.to_csv('minimum_charge_rate.csv')
c.to_csv('totalprecent_charge_rate.csv')

a, b, c = calc_parameter_error("efficiency", 5, 5)
a.to_csv('maximum_efficiency.csv')
b.to_csv('minimum_efficiency.csv')
c.to_csv('totalprecent_efficiency.csv')

a, b, c = calc_parameter_error("decay_rate", 5, 5)
a.to_csv('maximum_decay_rate.csv')
b.to_csv('minimum_decay_rate.csv')
c.to_csv('totalprecent_decay_rate.csv')

