import datetime
import math
import df_objects
import state
from abc import ABC


class DailyStrategy(ABC):
    def __call__(self, demand: df_objects.DemandHourly, state: state.State):
        pass


class GreedyDailyStrategy(DailyStrategy):
    def __call__(self, demand: df_objects.DemandHourly, state: state.State):
        simulation_result = [{"solar": 0, "storage": 0, "external_network": 0, "selling": 0}]
        state.batteries.sort(key=lambda battery: battery.efficiency, reverse=True)
        for hour in range(24):
            hourly_demand = demand.get_demand_daily_by_date(state.date)[hour]
            solar_production = sum([panel.calc_energy_gen_hourly(state.date)
                                    for panel in state.solar_panels])
            if solar_production >= hourly_demand:
                simulation_result[hour]["solar"] = hourly_demand

                to_charge = solar_production - hourly_demand
                battery_index = 0
                while math.isclose(to_charge, 0, abs_tol=10**-10) and battery_index < len(state.batteries):
                    charged = state.batteries[battery_index].try_charge(to_charge)
                    to_charge -= charged
                    battery_index += 1
                simulation_result[hour]["selling"] = to_charge
            else:
                simulation_result[hour]["solar"] = solar_production
                to_supply = hourly_demand - solar_production
                battery_index = 0
                while math.isclose(to_supply, 0, abs_tol=10 ** -10) and battery_index < len(state.batteries):
                    discharged = state.batteries[battery_index].try_discharge(to_supply)
                    to_supply -= discharged
                    battery_index += 1
                simulation_result[hour]["external_network"] = to_supply
            state.date += datetime.timedelta(hours=1)
        return simulation_result
