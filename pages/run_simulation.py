from imports import *
import period_strategy
from df_objects import *
from manager import Manager
import hourly_strategy
import time

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheLongCallbackManager(cache)

dash.register_page(__name__, background_callback_manager=background_callback_manager)

layout = html.Div([html.Progress(id="progress_bar", max=33),
                   dcc.Location(id="url"),
                   html.P(id="hidden")]
                  )


@callback(
    Output("url", "pathname"),
    Input("hidden", "id"),
    background=True,
    manager=background_callback_manager,
    progress=[Output("progress_bar", "value"), Output("progress_bar", "max")]
)
def process(set_progress, id):
    print("start")
    logging.info("Preprocess - Uploading files")
    demand_hourly = DemandHourlyStateData()
    solar_rad_hourly = SolarRadiationHourlyMonthData()
    logging.info("Preprocess - Files uploaded successfully")

    logging.info("Process - Start simulation")
    manager = Manager(demand_hourly, [period_strategy.PeriodStrategy(5000, 100)] * 33, [], solar_rad_hourly,
                      hourly_strategy.GreedyDailyStrategy())
    manager.run_simulator(set_progress)
    logging.info("Process - End simulation")

    logging.info("Postprocess - Start computing results")
    # post process
    logging.info("Postprocess - Start computing results")
    return "/show-energy-dist"
