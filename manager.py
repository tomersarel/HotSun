import os
import numpy as np
from config_manager import ConfigGetter
from df_objects import DemandHourlyStateData, SolarRadiationHourly, SolarRadiationHourlyMonthData, \
    SolarProductionHourlyDataPVGIS
import pandas as pd
import period_strategy
from df_objects import DemandHourly, SolarRadiationHourly
from period_strategy import PeriodStrategy
from periodic_simulation import PeriodicSimulation
from typing import Callable, List
from imports import *
from tqdm import tqdm
from state import State

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')


class Manager:
    """
    manages the activation of the periodic-simulation.
    saves the returned data.
    """

    def __init__(self,
                 hourly_electricity_demand: DemandHourly,
                 objects_period_strategy: list[period_strategy.PeriodStrategy],
                 periodic_available_area: np.array,
                 hourly_solar_radiation: SolarRadiationHourly,
                 daily_strategy: Callable, config: dict):
        """
        initializing the Manager object.
        :param hourly_electricity_demand: a hourly forecast for the electricity demand
        :param objects_period_strategy: the amount of solar panels and batteries which will be added in each period
        :param periodic_available_area: used in order to check that the addition strategy is doable
        :param hourly_solar_radiation: used to calculate the production of the solar panels
        :param daily_strategy: a function which manages the energy for each year
        """
        super().__init__()
        self.config = config
        time_string_format = self.config["TIME_FORMAT"]
        self.periods_length_in_days = self.config["PERIODS_DAYS_AMOUNT"]
        self.start_date = datetime.datetime.strptime(self.config["START_DATE"], time_string_format)
        end_date = datetime.datetime.strptime(self.config["END_DATE"], time_string_format)
        self.periods_amount = (end_date - self.start_date).days // self.periods_length_in_days
        self.hourly_electricity_demand = hourly_electricity_demand
        strategy = pd.DataFrame.from_dict(config["STRATEGY"])
        self.objects_period_strategy = [period_strategy.PeriodStrategy(row["solar_panel_purchased"], row["batteries_purchased"]) for index, row in strategy.iterrows()]
        self.periodic_available_area = periodic_available_area
        self.hourly_solar_radiation = hourly_solar_radiation
        self.daily_strategy = daily_strategy
        self.current_state = State(self.start_date)
        logging.info(f"Manager was built successfully.")


    def run_simulator(self, set_progress) -> pd.DataFrame:
        """
        activates the simulator for all the time-periods: prepare the data, call the simulator and saves the output
        :return: None
        """
        logging.info(f"Manager: starts simulation")
        output = []

        bar = tqdm(range(self.periods_amount))
        for period_i in bar:
            logging.info(f"Manager: enters {period_i} period of the simulation.")
            # create the period simulation object
            demand, solar_rad = self.slice_data_for_period(period_i)
            periodic_simulation = PeriodicSimulation(self.current_state, self.periods_length_in_days, demand, solar_rad,
                                                     self.objects_period_strategy[period_i], self.daily_strategy, self.config)
            # activate the simulation for this period
            periodic_simulation.start()

            simulation_output_data, self.current_state = periodic_simulation.get_result()
            output.append(simulation_output_data)
            set_progress((str(period_i + 1), str(self.periods_amount), "Running Simulation...", f"{round((period_i + 1) / self.periods_amount * 100)}%"))

        output = pd.concat(output)
        output.reset_index(inplace=True, drop=True)
        return output

    def slice_data_for_period(self, period_i: int):
        """
        gets the data which is relevant to the given period
        :param period_i: the index of the current period
        :return: 2 np 2-dimensions arrays, one for the demand, and second for the solar_rad
        """
        period_start_date, period_end_date = self.convert_period_index_to_dates(period_i)
        return self.hourly_electricity_demand.get_demand_hourly_by_range_of_date(period_start_date, period_end_date), \
            self.hourly_solar_radiation.get_solar_rad_daily_by_range_of_date(period_start_date, period_end_date)

    def save_output(self, period_i: int, simulation_output_data: pd.DataFrame) -> None:
        """
        saves the current state in a csv file, according to periods
        :param period_i: the index of the current period
        :param simulation_output_data: the data which was produced by the simulation
        :return: None
        """
        simulation_output_data.to_csv(f'simulation output/period{period_i}.csv', index=False)
        logging.info(f"Manager: the data was saved successfully.")

    def convert_period_index_to_dates(self, period_i: int) -> (datetime, datetime):
        """
        convert period index to the start date of the period and the end date of the period.
        :param period_i: the index of the period
        :return: the start date of the period and the end date of the period.
        """
        period_start_date = self.start_date + datetime.timedelta(days=self.periods_length_in_days) * period_i
        period_end_date = self.start_date + datetime.timedelta(days=self.periods_length_in_days) * (period_i + 1)
        return period_start_date, period_end_date

