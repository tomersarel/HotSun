import numpy as np

from imports import *
import period_strategy


class PeriodicSimulation:
    def __init__(self, state: State, period_length: int, demand: np.array, solar_rad: np.array,
                 periodic_strategy: period_strategy, daily_simulator: callable, config: dict):
        self.start_date = state.current_date
        self.end_date = state.current_date + datetime.timedelta(days=period_length)
        self.state = state
        self.demand = demand
        self.solar_rad = solar_rad
        self.daily_simulator = daily_simulator
        self.result = pd.DataFrame(
            columns=['Date', 'Batteries', 'Solar', 'Buying', 'Selling', 'Lost', 'Storaged', "NewBatteries",
                     "AllBatteries", "NewSolarPanels", "AllSolarPanels"])
        self.state.batteries.append(Battery(periodic_strategy.batteries, self.start_date, config))
        self.state.solar_panels.append(SolarPanel(periodic_strategy.solar_panels, config))
    
    
    def start(self):
        logging.info(f"Start periodic simulation {self.start_date}-{self.end_date}")

        for daily_demand, daily_solar_rad in zip(self.demand, self.solar_rad):
            day_result, self.state = self.daily_simulator(self.state, daily_demand, daily_solar_rad)
            self.result = pd.concat([self.result, day_result], ignore_index=True)

    def get_result(self):
        return self.result, self.state
