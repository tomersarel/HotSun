import math
import matplotlib.pyplot as plt
from distutils.command.config import config
import pandas as pd
import numpy as np
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


d = pd.read_csv("Sumenergy.csv")
original_df = manager.run_simulator(n)
original_df.drop('Date', axis='columns', inplace=True)
original_df.to_csv('original_data')


def calc_parameter_error(name, percent, amount):
    # create a numpy array with every parameter value
    name_set = np.linspace(ConfigGetter["battery"][name] * ((100 - percent) / 100),
                           ConfigGetter["battery"][name] * ((100 + percent) / 100), amount)
    arr = []

    # running the simulation for each value in name_set
    for i in name_set:
        # defining the parameter
        ConfigGetter["battery"][name] = i
        # running the simulation
        tmp = manager.run_simulator(n)
        # dropping the date column (numpy don't work with '-')
        tmp.drop('Date', axis='columns', inplace=True)
        # converting the csv from the simulation to numpy (it comes in pandas)
        np_a = tmp.to_numpy()
        arr.append(np_a)

    simulation_arr = np.stack(arr)

    # take the minimum of each hour for each parameter
    minimum_values = np.min(simulation_arr, axis=0)
    # take the maximum of each hour for each parameter
    maximum_values = np.max(simulation_arr, axis=0)

    # the final minimum pandas
    minimum_df = pd.DataFrame(minimum_values, columns=['Batteries', 'Solar', 'Buying',
                                                       'Selling', 'Lost', 'Storaged',
                                                       'NewBatteries', 'AllBatteries',
                                                       'NewSolarPanels', 'AllSolarPanels'])
    # the final maximum pandas
    maximum_df = pd.DataFrame(maximum_values, columns=['Batteries', 'Solar', 'Buying',
                                                       'Selling', 'Lost', 'Storaged',
                                                       'NewBatteries', 'AllBatteries',
                                                       'NewSolarPanels', 'AllSolarPanels'])

    # converting the normal pandas to numpy
    np_original = original_df.to_numpy()
    # taking the inverse for each box != 0
    reciprocal_values = np.reciprocal(np_original, where=np_original != 0)
    # return to pandas
    pd_df_with_nones = pd.DataFrame(reciprocal_values)
    # replace nan with 0
    pd_df_with_nones.fillna(0, inplace=True)
    # back to numpy
    reciprocal_values = pd_df_with_nones.to_numpy()

    # calculating the percent of different
    total_percent = (maximum_values - minimum_values) * reciprocal_values * 100
    up_percent = (maximum_values - np_original) * reciprocal_values * 100
    down_percent = (np_original - minimum_values) * reciprocal_values * 100

    # convert to pandas
    total_percent = pd.DataFrame(total_percent)
    up_percent = pd.DataFrame(up_percent)
    down_percent = pd.DataFrame(down_percent)

    # put down to a list
    frames = [total_percent, up_percent, down_percent]

    # convert to a pandas DataFrame
    final_percent = pd.concat(frames)

    # return in the order: maximum, minimum, percent
    return maximum_df, minimum_df, final_percent


csv_of_maximum_for_each_parameter_each_hour, csv_of_minimum_for_each_parameter_each_hour, \
    csv_of_total_than_upp_than_down_percent_between_the_maximum_and_minimum = calc_parameter_error("capacity", 5, 5)
csv_of_maximum_for_each_parameter_each_hour.to_csv('maximum_capacity.csv')
csv_of_minimum_for_each_parameter_each_hour.to_csv('minimum_capacity.csv')
csv_of_total_than_upp_than_down_percent_between_the_maximum_and_minimum.to_csv('totalprecent_capacity.csv')

csv_of_maximum_for_each_parameter_each_hour, csv_of_minimum_for_each_parameter_each_hour, \
    csv_of_total_than_upp_than_down_percent_between_the_maximum_and_minimum = calc_parameter_error("lifetime", 5, 5)
csv_of_maximum_for_each_parameter_each_hour.to_csv('maximum_lifetime.csv')
csv_of_minimum_for_each_parameter_each_hour.to_csv('minimum_lifetime.csv')
csv_of_total_than_upp_than_down_percent_between_the_maximum_and_minimum.to_csv('totalprecent_lifetime.csv')

csv_of_maximum_for_each_parameter_each_hour, csv_of_minimum_for_each_parameter_each_hour, \
    csv_of_total_than_upp_than_down_percent_between_the_maximum_and_minimum = calc_parameter_error("charge_rate", 5, 5)
csv_of_maximum_for_each_parameter_each_hour.to_csv('maximum_charge_rate.csv')
csv_of_minimum_for_each_parameter_each_hour.to_csv('minimum_charge_rate.csv')
csv_of_total_than_upp_than_down_percent_between_the_maximum_and_minimum.to_csv('totalprecent_charge_rate.csv')

csv_of_maximum_for_each_parameter_each_hour, csv_of_minimum_for_each_parameter_each_hour, \
    csv_of_total_than_upp_than_down_percent_between_the_maximum_and_minimum = calc_parameter_error("efficiency", 5, 5)
csv_of_maximum_for_each_parameter_each_hour.to_csv('maximum_efficiency.csv')
csv_of_minimum_for_each_parameter_each_hour.to_csv('minimum_efficiency.csv')
csv_of_total_than_upp_than_down_percent_between_the_maximum_and_minimum.to_csv('totalprecent_efficiency.csv')

csv_of_maximum_for_each_parameter_each_hour, csv_of_minimum_for_each_parameter_each_hour, \
    csv_of_total_than_upp_than_down_percent_between_the_maximum_and_minimum = calc_parameter_error("decay_rate", 5, 5)
csv_of_maximum_for_each_parameter_each_hour.to_csv('maximum_decay_rate.csv')
csv_of_minimum_for_each_parameter_each_hour.to_csv('minimum_decay_rate.csv')
csv_of_total_than_upp_than_down_percent_between_the_maximum_and_minimum.to_csv('totalprecent_decay_rate.csv')