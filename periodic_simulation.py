import numpy as np

from imports import *
import period_strategy


class PeriodicSimulation:
    def __init__(self, state: State, period_length: int, demand: np.array, solar_rad: np.array,
                 periodic_strategy: period_strategy, daily_simulator: callable):
        self.start_date = state.current_date
        self.end_date = state.current_date + datetime.timedelta(days=period_length)
        self.state = state
        self.demand = demand
        self.solar_rad = solar_rad
        self.daily_simulator = daily_simulator
        self.result = pd.DataFrame(columns=['Date', 'Batteries', 'Solar', 'Buying', 'Selling', 'Lost'])

        self.state.batteries.append(Battery(periodic_strategy.batteries, 1, 1, 1, self.start_date))
        self.state.solar_panels.append(SolarPanel(periodic_strategy.solar_panels, 0.2, 1, 1))

    def start(self):
        logging.info(f"Start periodic simulation {self.start_date}-{self.end_date}")

        for daily_demand, daily_solar_rad in zip(self.demand, self.solar_rad):
            day_result, self.state = self.daily_simulator(self.state, daily_demand, daily_solar_rad)
            self.result = self.result.append(day_result, ignore_index=True)

            # TODO: kill batteries and solar panels

    def get_result(self):
        return self.result, self.state
