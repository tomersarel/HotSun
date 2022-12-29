from imports import *
import period_strategy
from df_objects import *
from manager import Manager
import hourly_strategy
import time
import sys

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheLongCallbackManager(cache)

dash.register_page(__name__, background_callback_manager=background_callback_manager)

layout = html.Div([html.Div([html.H3("Loading..."),
                    dbc.Progress(id="progress_bar"),
                  dcc.Interval(id='timer_progress', interval=1000),
                  dcc.Location(id='url')],
                  style={'position': 'absolute', 'top': '50%', 'left': '50%', 'margin-top': '0px', 'margin-left': '-150px', 'width': '300px', 'height': '100px', 'text-align': "center"}
                  ), html.P(id="hidden")], id='main')


@callback(
    Output("url", "href"),
    Input("url", "href"),
    background=True,
    manager=background_callback_manager
)
def process(id):
    std_err_backup = sys.stderr
    file_prog = open('progress.txt', 'w')
    sys.stderr = file_prog
    print("start")
    logging.info("Preprocess - Uploading files")
    demand_hourly = DemandHourlyStateData()
    solar_rad_hourly = SolarRadiationHourlyMonthData()
    logging.info("Preprocess - Files uploaded successfully")

    logging.info("Process - Start simulation")
    manager = Manager(demand_hourly, [period_strategy.PeriodStrategy(5000, 100)] * 33, [], solar_rad_hourly,
                      hourly_strategy.GreedyDailyStrategy())
    manager.run_simulator()
    logging.info("Process - End simulation")

    logging.info("Postprocess - Start computing results")
    # post process
    logging.info("Postprocess - Start computing results")

    file_prog.truncate()
    file_prog.close()
    sys.stderr = std_err_backup

    return "/show-energy-dist"


@callback(
    Output('progress_bar', 'value'),
    Input('timer_progress', 'n_intervals'),
    prevent_initial_call=True)
def callback_progress(n_intervals: int) -> (float, str):
    percent = 0
    try:
        with open('progress.txt', 'r') as file:
            str_raw = file.read()
        last_line = list(filter(None, str_raw.split('\n')))[-1]
        percent = float(last_line.split('%')[0])
    except:
        percent = 0
    finally:
        text = f'{percent:.0f}%'
        return percent
