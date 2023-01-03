from imports import *
import period_strategy
from df_objects import *
from manager import Manager
import hourly_strategy
import sys
import os

if os.path.exists("progress.txt"):
    os.remove("progress.txt")

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheLongCallbackManager(cache)
dash.register_page(__name__, background_callback_manager=background_callback_manager)

sidebar = html.Div([html.H4("Control Panel"),
                    dbc.Button("Run", id="run", color="primary", style={"width": "80%"}),
                    dbc.Button("Cancel", id="cancel", color="primary", style={"width": "80%"}),
                    html.Div()],
                   style={"height": "92vh"}, className="text-center")
display_summery = html.Div([
    dbc.Card([dbc.CardBody([
        html.H1(f"{i * 75 % 129}$", className="card-title", style={"text-align": "center", "font-size": 48}),
        html.H4(f"Parameter {i}", className="card-title", style={"text-align": "center"}),
        html.P(
            "description of the paramter",
            className="card-text",
        )])], style={"width": "18rem"}, className="mx-2 my-2") for i in range(8)
], className="row")
display_energy = html.Div([dcc.Slider(id="period_slider",
                                      min=ConfigGetter["START_YEAR"],
                                      max=ConfigGetter["END_YEAR"],
                                      step=1,
                                      marks={i: '{}'.format(i) for i in
                                             range(ConfigGetter["START_YEAR"], ConfigGetter["END_YEAR"])},
                                      value=ConfigGetter["START_YEAR"]),
                           dcc.Graph(id='yearlyGraph', style={"height": "600px"}),
                           dcc.Graph(id='dailyGraph', style={"display": "None"})
                           ])
display_finance = html.Div()

display = html.Div([dbc.Accordion([dbc.AccordionItem(display_summery, title='Summery'),
                                   dbc.AccordionItem(display_energy, title='Energy'),
                                   dbc.AccordionItem(display_finance, title='Finance')],
                                  always_open=True),

                    ], style={"overflow": "auto", "height": "92vh"})

layout = html.Div([dbc.Row([dbc.Col(sidebar, width=2),
                            dbc.Col(display, width=10)]),
                   html.Div([html.Div([html.H3("Loading..."),
                                       dbc.Progress(id="progress_bar", style={'width': '300px', 'height': '20px'})],
                                      style={"position": "absolute", "left": "50%", "top": "50%", "margin-top": "-50px",
                                             "margin-left": "-150px"}),
                             dcc.Interval(id='timer_progress', interval=1000),
                             dcc.Location(id='url')], id="loading")])

loading_style = {"display": 'block', 'position': 'absolute',
                 'top': '8%', 'left': '16%',
                 'text-align': "center", 'width': "84%", "height": "92%",
                 "background": "rgba(255,255,255,0.8)", "background-size": "cover"}


def generate_year_enr_graph(year):
    data = pd.read_csv(f"simulation output//period{year - ConfigGetter['START_YEAR']}.csv", parse_dates=['Date'],
                       dayfirst=True,
                       index_col=['Date'])
    data = data.resample('D').sum()
    return [go.Bar(x=data.index, y=data[col], name=col) for col in data.columns]


@callback(
    Output('yearlyGraph', 'figure'),
    Input('period_slider', 'value'))
def update_yearly_graph(value):
    return go.Figure(data=generate_year_enr_graph(value),
                     layout=go.Layout(barmode='stack', title=f"{value} energy distribution"))


def generate_day_enr_graph(date):
    df = pd.read_csv(f"simulation output//period{date.year - 2017}.csv", parse_dates=['Date'], dayfirst=True,
                     index_col=['Date'])
    df = df[(df.index >= date) & (df.index < date + datetime.timedelta(days=1))]
    return [go.Bar(x=df.index.hour, y=df[col], name=col) for col in df.columns]


@callback(
    Output('dailyGraph', 'figure'),
    Output('dailyGraph', 'style'),
    Input('yearlyGraph', 'clickData'),
    prevent_initial_call=True
)
def update_daily_graph(clickData):
    date = datetime.datetime.strptime(clickData['points'][0]['x'], "%Y-%m-%d")
    return go.Figure(data=generate_day_enr_graph(date),
                     layout=go.Layout(barmode='stack', title=f"{date.strftime('%d/%m/%Y')} energy distribution")), {
               "display": "block"}


@callback(
    Output("url", "pathname"),
    Input("run", "n_clicks"),
    manager=background_callback_manager,
    running=[
        (Output("run", "disabled"), True, False),
        (Output("cancel", "disabled"), False, True)],
    cancel=[Input("cancel_button_id", "n_clicks")],
    prevent_initial_call=True
)
def process(n_clicks):
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
    Output('progress_bar', 'label'),
    Output("loading", "style"),
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
        return percent, text, {"display": "None"} if percent in [0, 100] else loading_style
