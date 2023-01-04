import numpy as np

from manager import Manager
from df_objects import DemandHourlyStateData, SolarRadiationHourly
import period_strategy
import state
import hourly_strategy


def initialize_manager():
    periods_amount = 0  # todo: insert the real value
    hourly_electricity_demand = DemandHourlyStateData()
    objects_period_strategy = []
    # todo: add object to this ^
    periodic_available_area = np.zeros(periods_amount)
    hourly_solar_radiation = SolarRadiationHourly()
    daily_strategy = hourly_strategy.hourly_strategy_for_manager_test
    return Manager(hourly_electricity_demand, objects_period_strategy, periodic_available_area,
                   hourly_solar_radiation, daily_strategy)


def main():
    manager = initialize_manager()


if __name__ == "__main__":
    main()
