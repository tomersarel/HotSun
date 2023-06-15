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
            to_charge = solar_production - hourly_demand
            if solar_production >= hourly_demand:
                solar[hour] = hourly_demand

                battery_index = 0
                # if should_sell is true, sell the excess energy to the grid instead of storing it
                if self.should_sell:
                    selling[hour] = to_charge
                else:
                    while not math.isclose(to_charge, 0, abs_tol=10 ** -10) and battery_index < len(state.batteries):
                        charged = state.batteries[battery_index].try_charge(to_charge*0.8)
                        storaged[hour] += charged
                        to_charge -= charged
                        battery_index += 1
                        selling[hour] += charged
            else:
                solar[hour] = solar_production
                to_supply = hourly_demand - solar_production - to_charge
                battery_index = 0
                # if should_sell is false, buy the energy from the grid instead of discharging it
                while not math.isclose(to_supply, 0, abs_tol=10 ** -10) and battery_index < len(state.batteries):
                    discharged = state.batteries[battery_index].try_discharge(to_supply)
                    to_supply -= discharged
                    buying[hour] +=discharged
                    batteries[hour] += discharged
                    battery_index += 1
            
            state.current_date+= datetime.timedelta(hours=1)

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
        self.state = None
    def __call__(self, state: state.State, demand: np.array, solar_rad: np.array):
        batteries = [0] * 24
        solar = [0] * 24
        buying = [0] * 24
        selling = [0] * 24
        storaged = [0] * 24
        self.state = state
        self.state.batteries.sort(key=lambda battery: battery.efficiency, reverse=True)

        for hour in range(24):
            hourly_demand = demand[hour]
            solar_production = sum([panel.calc_energy_gen_hourly(solar_rad[hour])
                                    for panel in self.state.solar_panels])
            
            if solar_production >= hourly_demand:
                solar[hour] = hourly_demand

                to_charge = solar_production - hourly_demand
                battery_index = 0
                while not math.isclose(to_charge, 0, abs_tol=10 ** -10) and battery_index < len(self.state.batteries):
                    charged = self.state.batteries[battery_index].try_charge(to_charge)
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
            self.state.current_date += datetime.timedelta(hours=1)

        new_batteries_energy = self.state.batteries[-1].capacity
        new_panels_power = self.state.solar_panels[-1].amount * self.state.solar_panels[-1].max_power

        result = pd.DataFrame({'Date': [self.state.current_date + datetime.timedelta(hours=i) for i in range(24)],
                              'Batteries': batteries, 'Solar': solar, 'Buying': buying, 'Selling': selling,
                              'Lost': [0] * 24, 'Storaged': storaged,
                              "NewBatteries": [new_batteries_energy] * 24,
                              "AllBatteries": [len(self.state.batteries)] * 24,
                              "NewSolarPanels": [new_panels_power] * 24,
                              "AllSolarPanels": [len(self.state.solar_panels)] * 24})

        return result, self.state


class Manager(DailyStrategy):
    def __init__(self, period):
        if not period:
            raise ValueError("Period array cannot be empty")
        if not all(isinstance(p, bool) for p in period):
            raise TypeError("Period array must contain only boolean values")
        self.sell_rate = 0.9
        self.buy_rate = 1.1
        self.period = period
        self.should_sell = True
        self.economic_greedy_algorithm = EconomicGreedyStrategy(sell_rate=self.sell_rate, buy_rate=self.buy_rate, should_sell=self.should_sell)
        self.green_energy_utilization_algorithm = GreenEnergyUtilizationStrategy(buy_rate=self.sell_rate, sell_rate=self.buy_rate)
        self.flag = False
        self.state1 = None
        self.state2 = None
        self.result = pd.DataFrame()

    def getCurrentPeriodLength(self):
        if not self.period:
            raise ValueError("Period array cannot be empty")
        if not all(isinstance(p, bool) for p in self.period):
            raise TypeError("Period array must contain only boolean values")
        period_length = 0
        for i in range(len(self.period)):
            if self.period[i] == True:
                period_length += 1
            else:
                break
        return period_length
    
    def get_stating_preparation_time(self):
        if not self.state:
            raise ValueError("State parameter cannot be None")
        time_needed = 0
        period_length = self.getCurrentPeriodLength()
        for battery in self.state.batteries:
            time_needed += battery.get_max_charge()
        return time_needed

    def end_of_period(self):
        if not self.period:
            raise ValueError("Period array cannot be empty")
        if not all(isinstance(p, bool) for p in self.period):
            raise TypeError("Period array must contain only boolean values")
        period_length = self.getCurrentPeriodLength()
        if self.period[period_length - 1] == True and self.period[period_length] == False:
            self.should_sell = True
        elif self.period[period_length - 1] == False and self.period[period_length] == True:
            self.should_sell = False
        else:   
            self.should_sell = True

    def __call__(self, state: state.State, demand: np.array, solar_rad: np.array):
        if not state:
            raise ValueError("State parameter cannot be None")
        self.state = state
        try:
            for i in range(len(self.period)):
                if i == self.get_stating_preparation_time():
                    self.end_of_period()
                    self.flag = True
                if self.flag == True:
                    if self.should_sell == True:
                        self.result = self.economic_greedy_algorithm(state, demand, solar_rad)
                    else:
                        self.result,final_state = self.green_energy_utilization_algorithm(state, demand, solar_rad)
                else:
                    self.result,final_state = self.economic_greedy_algorithm(state, demand, solar_rad)
                if self.result['Buying'].sum() < self.result['Selling'].sum():
                    self.result = self.economic_greedy_algorithm(state, demand, solar_rad)
                else:
                    self.result,final_state = self.green_energy_utilization_algorithm(state, demand, solar_rad)
                state = final_state
        except Exception as e:
            return {"error": str(e)}, state
        # align dash.exceptions.LongCallbackError: An error occurred inside a long callback: shapes (864,) and (8760,) not aligned: 864 (dim 0) != 8760 (dim 0)

        return self.result, state

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
