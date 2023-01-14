import period_strategy
from df_objects import *
from imports import *
import manager
import hourly_strategy
from post_processor import PostProcessor
from matplotlib import pyplot as plt
import plotly
import dash

logging.info("Start application")

ConfigGetter.load_data()

logging.info("Preprocess - Uploading files")
# todo: move the loading of the post processor data to here
demand_hourly = DemandHourlyStateData()
solar_rad_hourly = SolarRadiationHourlyMonthData()
logging.info("Preprocess - Files uploaded successfully")

logging.info("Process - Start simulation")
manager = manager.Manager(demand_hourly, [period_strategy.PeriodStrategy(5000, 100)] * 33, [], solar_rad_hourly, hourly_strategy.GreedyDailyStrategy())
manager.run_simulator()
logging.info("Process - End simulation")

logging.info("Postprocess - Start computing results")
# post process
post_processor = PostProcessor()
total_income = post_processor.run_post_processor()
print(total_income)

logging.info("GUI - Show results")
# GUI

pd.options.plotting.backend = "plotly"

for i in range(33):
    data = pd.read_csv(f"simulation output//period{i}.csv", parse_dates=['Date'], dayfirst=True, index_col=['Date'])
    data_daily = data.resample('D').sum()
    fig = data_daily.plot.bar(title=f"{2017 + i}")
    fig.show()
    input()
