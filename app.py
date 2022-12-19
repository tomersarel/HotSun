import period_strategy
from df_objects import *
from imports import *
import manager
import hourly_strategy

logging.info("Start application")

ConfigGetter.load_data()

logging.info("Preprocess - Uploading files")
demand_hourly = DemandHourlyStateData()
solar_rad_hourly = SolarRadiationHourlyMonthData()
logging.info("Preprocess - Files uploaded successfully")

logging.info("Process - Start simulation")
manager = manager.Manager(demand_hourly, [period_strategy.PeriodStrategy(10, 10), period_strategy.PeriodStrategy(20, 10)], [], solar_rad_hourly, hourly_strategy.generic_hourly_strategy)
manager.run_simulator()
logging.info("Process - End simulation")

logging.info("Postprocess - Start computing results")
# post process
logging.info("Postprocess - Start computing results")

logging.info("GUI - Show results")
# GUI
