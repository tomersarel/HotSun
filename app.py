from df_objects import *
from imports import *

logging.info("Start application")

logging.info("Preprocess - Uploading files")
demand_hourly = DemandHourlyStateData()
solar_rad_hourly = SolarRadiationHourlyMonthData()
logging.info("Preprocess - Files uploaded successfully")

logging.info("Process - Start simulation")
# simulation
logging.info("Process - End simulation")

logging.info("Postprocess - Start computing results")
# post process
logging.info("Postprocess - Start computing results")

logging.info("GUI - Show results")
# GUI
