import datetime
import math
import df_objects
import state
from abc import ABC
import unittest
import numpy as np
from df_objects import *
from state import State


class DailyStrategy(ABC):
    def __call__(self, state: state.State, demand: np.array, solar: np.array):
        pass


class EconomicGreedyStrategy(DailyStrategy):
    def __init__(self, buy_rate: float, sell_rate: float, should_sell: bool = False):
        self.buy_rate = buy_rate
        self.sell_rate = sell_rate
        self.should_sell = should_sell

    def __call__(self, state: state.State, demand: np.array, solar_rad: np.array):
        batteries = [0] * 24
        solar = [0] * 24
        buying = [0] * 24
        selling = [0] * 24
        storaged = [0] * 24
        state.batteries.sort(key=lambda battery: battery.efficiency, reverse=True)

        for hour in range(24):
            hourly_demand = demand[hour]
            solar_production = sum([panel.calc_energy_gen_hourly(solar_rad[hour])
                                    for panel in state.solar_panels])
            if solar_production > hourly_demand:
                solar[hour] = hourly_demand

                to_charge = solar_production - hourly_demand
                battery_index = 0
                # if should_sell is true, sell the excess energy to the grid instead of storing it
                if self.should_sell:
                    selling[hour] = to_charge
                else:
                    while not math.isclose(to_charge, 0, abs_tol=10 ** -10) and battery_index < len(state.batteries):
                        charged = state.batteries[battery_index].try_charge(to_charge)
                        storaged[hour] += charged
                        to_charge -= charged
                        battery_index += 1
            else:
                solar[hour] = solar_production
                to_supply = hourly_demand - solar_production
                battery_index = 0
                # if should_sell is false, buy the energy from the grid instead of discharging it
                if self.should_sell:
                    buying[hour] = to_supply
                else:
                    while not math.isclose(to_supply, 0, abs_tol=10 ** -10) and battery_index < len(state.batteries):
                        discharged = state.batteries[battery_index].try_discharge(to_supply)
                        to_supply -= discharged
                        batteries[hour] += discharged
                        battery_index += 1
            state.current_date += datetime.timedelta(hours=1)

        new_batteries_energy = state.batteries[-1].capacity
        new_panels_power = state.solar_panels[-1].amount * state.solar_panels[-1].max_power

        result = pd.DataFrame({'Date': [state.current_date + datetime.timedelta(hours=i) for i in range(24)],
                              'Batteries': batteries, 'Solar': solar, 'Buying': buying, 'Selling': selling,
                              'Lost': [0] * 24, 'Storaged': storaged,
                              "NewBatteries": [new_batteries_energy] * 24,
                              "AllBatteries": [len(state.batteries)] * 24,
                              "NewSolarPanels": [new_panels_power] * 24,
                              "AllSolarPanels": [len(state.solar_panels)] * 24})

        return result, state


class GreenEnergyUtilizationStrategy(DailyStrategy):
    def __init__(self, buy_rate: float, sell_rate: float):
        self.buy_rate = buy_rate
        self.sell_rate = sell_rate

    def __call__(self, state: state.State, demand: np.array, solar_rad: np.array):
        batteries = [0] * 24
        solar = [0] * 24
        buying = [0] * 24
        selling = [0] * 24
        storaged = [0] * 24
        state.batteries.sort(key=lambda battery: battery.efficiency, reverse=True)

        for hour in range(24):
            hourly_demand = demand[hour]
            solar_production = sum([panel.calc_energy_gen_hourly(solar_rad[hour])
                                    for panel in state.solar_panels])
            
            if solar_production > hourly_demand:
                solar[hour] = hourly_demand

                to_charge = solar_production - hourly_demand
                battery_index = 0
                while not math.isclose(to_charge, 0, abs_tol=10 ** -10) and battery_index < len(state.batteries):
                    charged = state.batteries[battery_index].try_charge(to_charge)
                    storaged[hour] += charged
                    to_charge -= charged
                    battery_index += 1
                print("to_charge: ", to_charge)
                selling[hour] = to_charge
            else:
                solar[hour] = solar_production
                to_supply = hourly_demand - solar_production
                battery_index = 0
                while not math.isclose(to_supply, 0, abs_tol=10 ** -10) and battery_index < len(state.batteries):
                    discharged = state.batteries[battery_index].try_discharge(to_supply)
                    to_supply -= discharged
                    batteries[hour] += discharged
                    battery_index += 1
                buying[hour] = to_supply
            state.current_date += datetime.timedelta(hours=1)

        new_batteries_energy = state.batteries[-1].capacity
        new_panels_power = state.solar_panels[-1].amount * state.solar_panels[-1].max_power

        result = pd.DataFrame({'Date': [state.current_date + datetime.timedelta(hours=i) for i in range(24)],
                              'Batteries': batteries, 'Solar': solar, 'Buying': buying, 'Selling': selling,
                              'Lost': [0] * 24, 'Storaged': storaged,
                              "NewBatteries": [new_batteries_energy] * 24,
                              "AllBatteries": [len(state.batteries)] * 24,
                              "NewSolarPanels": [new_panels_power] * 24,
                              "AllSolarPanels": [len(state.solar_panels)] * 24})

        return result, state


class Manager(DailyStrategy):
    # this algorithm returns the best result between the two algorithms passed as parameters as it provides the best of both words for the long run
    #self.economic_greedy_algorithm is EconomicGreedyStrategy
    #self.green_energy_utilization_algorithm is GreenEnergyUtilizationStrategy and they are known ahead of time
    def __init__(self, period):
        self.sell_rate = 0.9
        self.buy_rate = 1.1
        self.period = period
        self.should_sell = True
        self.economic_greedy_algorithm = EconomicGreedyStrategy(sell_rate=self.sell_rate, buy_rate=self.buy_rate, should_sell=self.should_sell)
        self.green_energy_utilization_algorithm = GreenEnergyUtilizationStrategy(buy_rate=self.sell_rate, sell_rate=self.buy_rate)
        self.flag = False
        self.state = None
    def getCurrentPeriodLength(self):
        # period is an array of boolean values which means true - high rate, false - low rate
        # calculate the length of the current period
        # if the current period is high rate, return the length of the high rate period
        # if the current period is low rate, return the length of the low rate period
        period_length = 0
        for i in range(len(self.period)):
            if self.period[i] == True:
                period_length += 1
            else:
                break
        return period_length
    
    def get_stating_preparation_time(self):
        # return the time needed to prepare for the next period and charge the batteries to full capacity
        time_needed = 0
        period_length = self.getCurrentPeriodLength()
        # go  over the batteries and calculate the time needed to charge them to full capacity
        for battery in self.state.batteries:
            time_needed += battery.get_max_charge()
        
        #return the time needed in hours
        return time_needed
    

    def end_of_period(self):
        #if the current period is high and going into low , sell all the energy in the batteries
        #if the current period is low and going into high, buy enough energy to fill the batteries
        #if the current period is high and going into high, do nothing
        #if the current period is low and going into low, do nothing
        period_length = self.getCurrentPeriodLength()
        if self.period[period_length - 1] == True and self.period[period_length] == False: # going from high to low 
            self.should_sell = True
        elif self.period[period_length - 1] == False and self.period[period_length] == True: # going from low to high
            self.should_sell = False
        else:   
            self.should_sell = True

    def __call__(self, state: state.State, demand: np.array, solar_rad: np.array):
        self.state = state
        #loop through the period and simulate the algorithm for each hour
        # if the current hour in the preiod index is the hour to begin charging, charge or sell fully the batteries according to the period
        # if the current hour is not the hour to begin charging, use the algorithms to calculate the energy to buy or sell
        # return the best result between the two algorithms passed as parameters as it provides the best of both words for the long run
        result = None
        for i in range(len(self.period)):
            if i == self.get_stating_preparation_time():
                self.end_of_period()
                self.flag = True
            if self.flag == True:
                if self.should_sell == True:
                    result = self.economic_greedy_algorithm(state, demand, solar_rad)
                else:
                    result,final_state = self.green_energy_utilization_algorithm(state, demand, solar_rad)
            else:
                result,final_state = self.economic_greedy_algorithm(state, demand, solar_rad)
        return result, final_state
   

class GreedyDailyStrategy(DailyStrategy):
    def __call__(self, state: state.State, demand: np.array, solar_rad: np.array):
        batteries = [0] * 24
        solar = [0] * 24
        buying = [0] * 24
        selling = [0] * 24
        storaged = [0] * 24
        state.batteries.sort(key=lambda battery: battery.efficiency, reverse=True)

        for hour in range(24):

            hourly_demand = demand[hour]
            solar_production = sum([panel.calc_energy_gen_hourly(solar_rad[hour])
                                    for panel in state.solar_panels])
            if solar_production >= hourly_demand:
                solar[hour] = hourly_demand

                to_charge = solar_production - hourly_demand
                battery_index = 0
                while not math.isclose(to_charge, 0, abs_tol=10 ** -10) and battery_index < len(state.batteries):
                    charged = state.batteries[battery_index].try_charge(to_charge)
                    storaged[hour] += charged
                    to_charge -= charged
                    battery_index += 1
                selling[hour] = to_charge
            else:
                solar[hour] = solar_production
                to_supply = hourly_demand - solar_production
                battery_index = 0
                while not math.isclose(to_supply, 0, abs_tol=10 ** -10) and battery_index < len(state.batteries):
                    discharged = state.batteries[battery_index].try_discharge(to_supply)
                    to_supply -= discharged
                    batteries[hour] += discharged
                    battery_index += 1
                    buying[hour] = to_supply
            state.current_date += datetime.timedelta(hours=1)

        new_batteries_energy = state.batteries[-1].capacity
        new_panels_power = state.solar_panels[-1].amount * state.solar_panels[-1].max_power

        result = pd.DataFrame({'Date': [state.current_date + datetime.timedelta(hours=i) for i in range(24)],
                              'Batteries': batteries, 'Solar': solar, 'Buying': buying, 'Selling': selling,
                              'Lost': [0] * 24, 'Storaged': storaged,
                              "NewBatteries": [new_batteries_energy] * 24,
                              "AllBatteries": [len(state.batteries)] * 24,
                              "NewSolarPanels": [new_panels_power] * 24,
                              "AllSolarPanels": [len(state.solar_panels)] * 24})
        # result = pd.DataFrame({'Date': [state.current_date + datetime.timedelta(hours=i) for i in range(24)],
        #                        'Batteries': 1, 'Solar': 1, 'Buying': 1, 'Selling': 1,
        #                        'Lost': [0] * 24, 'Storaged': 1,
        #                        "NewBatteries": [1] * 24,
        #                        "AllBatteries": [i + 1 for i in range(24)],
        #                        "NewSolarPanels": [1] * 24,
        #                        "AllSolarPanels": [i + 1 for i in range(24)]})

        return result, state


class GreedyTest(unittest.TestCase):
    def test_basic(self):
        # TODO : generalize the test
        # WARNING! This test is using dummy methods and should be removed when possible
        from battery import Battery
        from solar_panel import SolarPanel
        demand = df_objects.DemandHourlyStateData()
        cur_state = state.State(datetime.datetime.now())

        cur_state.batteries = [Battery(1, datetime.datetime(year=1, month=1, day=1)),
                               Battery(1, datetime.datetime(year=1, month=1, day=1))]
        cur_state.batteries[0].update_efficiency(datetime.datetime(year=2, month=1, day=1))
        cur_state.solar_panels = [SolarPanel(1, 1, 1, 1, 1), SolarPanel(1, 1, 1, 1, 1)]



def generic_hourly_strategy(state: State, demand: df_objects.DemandHourly, solar_rad: df_objects.SolarRadiationHourly):
    result = pd.DataFrame({'Date': [state.current_date + datetime.timedelta(hours=i) for i in range(24)],
                           'Batteries': [1] * 24, 'Solar': [1] * 24, 'Buying': [1] * 24, 'Selling': [1] * 24,
                           'Lost': [1] * 24})
    state.current_date += datetime.timedelta(days=1)
    return result, state
