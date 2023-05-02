import datetime
import math
import df_objects
import state
from abc import ABC
import unittest
import numpy as np


class DailyStrategy(ABC):
    def __call__(self, state: state.State, demand: np.array, solar: np.array):
        pass


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
                              "AllBatteriesCapacity": [sum([battery.capacity for battery in state.batteries])] * 24,
                              "AllBatteriesCharge": [sum([battery.current_energy for battery in state.batteries])] * 24,
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


from df_objects import *
from state import State


def generic_hourly_strategy(state: State, demand: df_objects.DemandHourly, solar_rad: df_objects.SolarRadiationHourly):
    result = pd.DataFrame({'Date': [state.current_date + datetime.timedelta(hours=i) for i in range(24)],
                           'Batteries': [1] * 24, 'Solar': [1] * 24, 'Buying': [1] * 24, 'Selling': [1] * 24,
                           'Lost': [1] * 24})
    state.current_date += datetime.timedelta(days=1)
    return result, state
