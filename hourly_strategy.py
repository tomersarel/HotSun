import datetime
import math
import df_objects
import state
from abc import ABC
import unittest


class DailyStrategy(ABC):
    def __call__(self, demand: df_objects.DemandHourlyStateData, state: state.State):
        # TODO: Change to city data
        pass


class GreedyDailyStrategy(DailyStrategy):
    def __call__(self, demand: df_objects.DemandHourlyStateData, state: state.State):
        simulation_result = []
        state.batteries.sort(key=lambda battery: battery.efficiency, reverse=True)
        for hour in range(24):
            simulation_result.append({"solar": 0, "storage": 0, "external_network": 0, "selling": 0})
            hourly_demand = demand.get_demand_daily_by_date(state.date)[hour]
            solar_production = sum([panel.calc_energy_gen_hourly(state.date)
                                    for panel in state.solar_panels])
            if solar_production >= hourly_demand:
                simulation_result[hour]["solar"] = hourly_demand

                to_charge = solar_production - hourly_demand
                battery_index = 0
                while not math.isclose(to_charge, 0, abs_tol=10**-10) and battery_index < len(state.batteries):
                    charged = state.batteries[battery_index].try_charge(to_charge)
                    to_charge -= charged
                    battery_index += 1
                simulation_result[hour]["selling"] = to_charge
            else:
                simulation_result[hour]["solar"] = solar_production
                to_supply = hourly_demand - solar_production
                battery_index = 0
                while not math.isclose(to_supply, 0, abs_tol=10 ** -10) and battery_index < len(state.batteries):
                    discharged = state.batteries[battery_index].try_discharge(to_supply)
                    to_supply -= discharged
                    simulation_result[hour]["storage"] += discharged
                    battery_index += 1
                simulation_result[hour]["external_network"] = to_supply
            state.date += datetime.timedelta(hours=1)
        return simulation_result


class GreedyTest(unittest.TestCase):
    def test_basic(self):
        #TODO : generalize the test
        #WARNING! This test is using dummy methods and should be removed when possible
        from battery import Battery
        from solar_panel import SolarPanel
        demand = df_objects.DemandHourlyStateData()
        cur_state = state.State(1, datetime.datetime.now(), datetime.datetime.now())

        cur_state.batteries = [Battery(1, datetime.datetime(year=1, month=1, day=1)), Battery(1, datetime.datetime(year=1, month=1, day=1))]
        cur_state.batteries[0].update_efficiency(datetime.datetime(year=2, month=1, day=1))
        cur_state.solar_panels = [SolarPanel(1,1,1,1), SolarPanel(1,1,1,1)]
        res = GreedyDailyStrategy()(demand, cur_state)
        print(res)


from df_objects import *
from state import State


def generic_hourly_strategy(state: State, demand: df_objects.DemandHourly, solar_rad: df_objects.SolarRadiationHourly):

    result = pd.DataFrame({'Date': [state.current_date + datetime.timedelta(hours=i) for i in range(24)],
                           'Batteries': [1] * 24, 'Solar': [1] * 24, 'Buying': [1] * 24, 'Selling': [1] * 24,
                           'Lost': [1] * 24})
    state.current_date += datetime.timedelta(days=1)
    return result, state

