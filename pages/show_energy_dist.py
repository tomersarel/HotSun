import time

from imports import *
import period_strategy
from df_objects import *
from manager import Manager
import hourly_strategy
import sys
import os

"""if os.path.exists("progress.txt"):
    os.remove("progress.txt")"""

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheLongCallbackManager(cache)
dash.register_page(__name__, background_callback_manager=background_callback_manager)

colors = {"Solar": "#ffe205", "Batteries": "gray", "Buying": "#ec4141", "Selling": "#5fbb4e", "Storaged": "#9edbf9",
          "Lost": "gray"}

sidebar = html.Div([html.H4("Control Panel"),
                    dbc.Button("Run", id="run", color="primary", style={"width": "50%"}, className="my-2 text-center"),
                    html.Div(id="paramerts", className="my-2"),
                    dcc.Store(id="df")],
                   style={"display": "None"}, id="sidebar", className="mx-3 my-3")


def generate_year_enr_graph(start_year, end_year, df, resample='D'):
    data = df[(df['Date'] >= datetime.datetime(year=start_year, day=1, month=1)) & (
                df['Date'] < datetime.datetime(year=end_year, day=1, month=1))]
    data = data.resample(resample, on='Date', convention="start").sum()
    return [go.Bar(x=data.index, y=data[col], name=col, marker={'color': colors[col], 'line.width': 0}) for col in
            data.columns]


def get_display(config, df):
    display_summery = html.Div([html.Div([
        dbc.Card([dbc.CardBody([
            html.H1(f"-", className="card-title", style={"text-align": "center", "font-size": 48}),
            html.H4(f"Parameter {i}", className="card-title", style={"text-align": "center"}),
            html.P(
                "description of the paramter",
                className="card-text",
            )])], style={"width": "18rem"}, className="mx-2 my-2") for i in range(8)
    ], className="row"),
        dcc.Graph(figure=go.Figure(
            data=generate_year_enr_graph(config['START_YEAR'], config['END_YEAR'], dict_to_dataframe(df), 'Y'),
            layout=go.Layout(barmode='stack', title=f"yearly energy distribution")))
    ])
    display_energy = html.Div([dcc.Slider(id="period_slider",
                                          min=config["START_YEAR"],
                                          max=config["END_YEAR"] - 1,
                                          step=1,
                                          marks={i: '{}'.format(i) for i in
                                                 range(config["START_YEAR"], config["END_YEAR"] - 1)},
                                          value=config["START_YEAR"]),
                               dcc.Graph(id='yearlyGraph', style={"height": "600px"}),
                               dcc.Graph(id='dailyGraph', style={"display": "None"})
                               ])
    display_finance = html.Div()

    display = html.Div([dbc.Accordion([dbc.AccordionItem(display_summery, title='Summery'),
                                       dbc.AccordionItem(display_energy, title='Energy'),
                                       dbc.AccordionItem(display_finance, title='Finance')],
                                      always_open=True),

                        ], style={"overflow": "auto", "height": "92vh"})
    return display


layout = html.Div([html.Div(id="placeholder"), dbc.Row([dbc.Col(sidebar, width=3),
                                                        dbc.Col(id="display", width=9)]),
                   html.Div([html.Div([html.H3("Loading..."),
                                       dbc.Progress(id="progress_bar", style={'width': '300px', 'height': '20px'})],
                                      style={"position": "absolute", "left": "50%", "top": "50%", "margin-top": "-50px",
                                             "margin-left": "-150px"}),
                             dcc.Interval(id='timer_progress', interval=1000),
                             dcc.Location(id='url')], id="loading"),
                   ])

loading_style = {"display": 'block', 'position': 'absolute',
                 'top': '8%', 'left': '0%',
                 'text-align': "center", 'width': "100%", "height": "92%",
                 "background": "rgba(255,255,255,0.8)", "background-size": "cover"}


def dict_to_dataframe(df):
    df = pd.DataFrame(df)
    if df.empty:
        return df
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df.set_index('Date')
    for coloumn in df.columns:
        if coloumn != "Date":
            df[coloumn] = pd.to_numeric(df[coloumn])
    return df


@callback(
    Output('yearlyGraph', 'figure'),
    Input('period_slider', 'value'),
    State("df", "data")
)
def update_yearly_graph(value, df):
    fig = go.Figure(data=generate_year_enr_graph(value, value + 1, dict_to_dataframe(df)),
                    layout=go.Layout(barmode='stack', title=f"{value} energy distribution"))
    fig.update_layout(bargap=0)
    return fig


def generate_day_enr_graph(date, df):
    df = df[(df['Date'] >= date) & (df['Date'] < date + datetime.timedelta(days=1))]
    df = df.set_index('Date')
    return [go.Bar(x=df.index.hour, y=df[col], name=col, marker={'color': colors[col], 'line.width': 0}) for col in df.columns]


@callback(
    Output('dailyGraph', 'figure'),
    Output('dailyGraph', 'style'),
    Input('yearlyGraph', 'clickData'),
    State("df", "data"),
    prevent_initial_call=True
)
def update_daily_graph(clickData, df):
    date = datetime.datetime.strptime(clickData['points'][0]['x'], "%Y-%m-%d")
    return go.Figure(data=generate_day_enr_graph(date, dict_to_dataframe(df)),
                     layout=go.Layout(barmode='stack', title=f"{date.strftime('%d/%m/%Y')} energy distribution")), {
               "display": "block"}


def get_parameters(config):
    result = []
    for parameter, value in config.items():
        if parameter not in ["START_YEAR", "END_YEAR", "PERIODS_DAYS_AMOUNT"]:
            parameter = parameter.replace("_", " ").lower().capitalize()
            if type(value) == int:
                result.append(dbc.Row([dbc.Col(f"{parameter}:", width="auto"), dbc.Col(dbc.Input(placeholder=f"{value}", type="number"))], className="my-2"))
            elif type(value) == dict:
                result.append(dbc.Row(dbc.Accordion(dbc.AccordionItem(get_parameters(value), title=parameter), start_collapsed=True)))
    return result


@callback(
    Output("paramerts", "children"),
    Output("df", "data"),
    Output("display", "children"),
Output("sidebar", "style"),
    Input("run", "n_clicks"),
    State("config", "data"),
    manager=background_callback_manager,
    running=[
        (Output("run", "children"), True, False),
        (Output("cancel", "disabled"), False, True)],
    cancel=[Input("cancel_button_id", "n_clicks")]
)
def process(n_clicks, config):
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
    output = manager.run_simulator()
    logging.info("Process - End simulation")

    logging.info("Postprocess - Start computing results")
    # post process
    logging.info("Postprocess - Start computing results")

    file_prog.truncate()
    file_prog.close()
    sys.stderr = std_err_backup
    return get_parameters(config), output.to_dict('records'), get_display(config, output), \
           {"height": "92vh", "width": "100%", "overflow-y": "auto", "overflow-x": "hidden"}


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
