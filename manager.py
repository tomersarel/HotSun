import os
import numpy as np
from config_manager import ConfigGetter
from df_objects import DemandHourlyStateData, SolarRadiationHourly, SolarRadiationHourlyMonthData, \
    SolarProductionHourlyDataPVGIS
import pandas as pd
import period_strategy
from df_objects import DemandHourlyStateData, SolarRadiationHourly
from process_manager import ProcessManager
from period_strategy import PeriodStrategy
from periodic_simulation import PeriodicSimulation
from typing import Callable, List
from imports import *
from tqdm import tqdm
from state import State

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')


class Manager(ProcessManager):
    """
    manages the activation of the periodic-simulation.
    saves the returned data.
    """


    def __init__(self,
                 hourly_electricity_demand: DemandHourlyStateData,
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
        self.hourly_electricity_demand = hourly_electricity_demand
        strategy = pd.DataFrame.from_dict(config["STRATEGY"])
        self.objects_period_strategy = [period_strategy.PeriodStrategy(row["solar_panel_purchased"], row["batteries_purchased"]) for index, row in strategy.iterrows()]
        self.periodic_available_area = periodic_available_area
        self.hourly_solar_radiation = hourly_solar_radiation
        self.daily_strategy = daily_strategy
        # prepare data for the simulation
        self.current_state = State(self.start_date)
        logging.info(f"Manager was built successfully.")


    def run_simulator(self) -> pd.DataFrame:
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
            # save the simulation output
            self.save_output(period_i, simulation_output_data)
            output.append(simulation_output_data)


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

