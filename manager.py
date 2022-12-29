import os
import numpy as np

from df_objects import DemandHourlyStateData, SolarRadiationHourly
from period_strategy import PeriodStrategy
from periodic_simulation import PeriodicSimulation
from typing import Callable, List
from imports import *
from tqdm import tqdm

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')


class Manager:
    """
    manages the activation of the periodic-simulation.
    saves the returned data.
    """

    def __init__(self,
                 hourly_electricity_demand: DemandHourlyStateData,
                 objects_period_strategy: List[PeriodStrategy],
                 periodic_available_area: np.array,
                 hourly_solar_radiation: SolarRadiationHourly,
                 daily_strategy: Callable):
        """
        initializing the Manager object.
        :param hourly_electricity_demand: a hourly forecast for the electricity demand
        :param objects_period_strategy: the amount of solar panels and batteries which will be added in each period
        :param periodic_available_area: used in order to check that the addition strategy is doable
        :param hourly_solar_radiation: used to calculate the production of the solar panels
        :param daily_strategy: a function which manages the energy for each year
        """
        self.hourly_electricity_demand = hourly_electricity_demand
        self.objects_period_strategy = objects_period_strategy
        self.periodic_available_area = periodic_available_area
        self.hourly_solar_radiation = hourly_solar_radiation
        self.daily_strategy = daily_strategy
        # giving default values to the data which will be read from the json
        self.periods_length_in_days = 0
        self.start_date = datetime.datetime.now()
        self.periods_amount = 0
        self.read_json_data()
        # prepare data for the simulation
        self.current_state = State(self.start_date)
        logging.info(f"Manager was built successfully.")

    def read_json_data(self):
        time_string_format = ConfigGetter["TIME_FORMAT"]
        self.periods_length_in_days = ConfigGetter["PERIODS_DAYS_AMOUNT"]
        # reads the start & end date as a datetime object
        self.start_date = datetime.datetime.strptime(ConfigGetter["START_DATE"], time_string_format)
        end_date = datetime.datetime.strptime(ConfigGetter["END_DATE"], time_string_format)
        self.periods_amount = (end_date - self.start_date).days // self.periods_length_in_days

    def run_simulator(self, set_progress) -> None:
        """
        activates the simulator for all the time-periods: prepare the data, call the simulator and saves the output
        :return: None
        """
        logging.info(f"Manager: starts simulation")
        for period_i in tqdm(range(self.periods_amount), desc="Loading...", ):
            logging.info(f"Manager: enters {period_i} period of the simulation.")
            # create the period simulation object
            demand, solar_rad = self.slice_data_for_period(period_i)
            periodic_simulation = PeriodicSimulation(self.current_state, self.periods_length_in_days, demand, solar_rad,
                                                     self.objects_period_strategy[period_i], self.daily_strategy)
            # activate the simulation for this period
            periodic_simulation.start()
            simulation_output_data, self.current_state = periodic_simulation.get_result()
            # save the simulation output
            self.save_output(period_i, simulation_output_data)

    def slice_data_for_period(self, period_i: int) -> (np.array, np.array):
        """
        gets the data which is relevant to the given period
        :param period_i: the index of the current period
        :return: 2 np 2-dimensions arrays, one for the demand, and second for the solar_rad
        """
        period_start_date = self.start_date + datetime.timedelta(days=self.periods_length_in_days) * period_i
        period_end_date = self.start_date + datetime.timedelta(days=self.periods_length_in_days) * (period_i + 1)
        return self.hourly_electricity_demand.get_demand_hourly_by_range_of_date(period_start_date, period_end_date), \
               self.hourly_solar_radiation.get_solar_rad_daily_by_range_of_date(period_start_date, period_end_date)

    def save_output(self, period_i: int, simulation_output_data: pd.DataFrame) -> None:
        """
        saves the current state in a csv file, according to periods
        :param period_i: the index of the current period
        :param simulation_output_data: the data which was produced by the simulation
        :return: None
        """
        logging.info(f"Manager: the data of the {period_i} period was saved successfully.")
        simulation_output_data.to_csv(f'simulation output/period{period_i}.csv', index=False)
