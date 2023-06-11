import datetime
import io
import json

import numpy
import pandas
import base64
from dash import dash_table
from datetime import datetime
from dash.exceptions import PreventUpdate
from imports import *

dash.register_page(__name__)


def get_strategy_graph(x, y, y_title, x_title):
    """
    generates a graph of the purchase strategy
    :param x: the x-axis
    :param y: the y-axis
    :param title: the title of the graph
    :param y_title: the y-axis title
    :param x_title: the x-axis title
    :return: the graph
    """
    return go.Figure(data=go.Scatter(x=x, y=y, mode='lines+markers'),
                     layout={
                         'plot_bgcolor': "rgba(0,0,0,0)",
                         'paper_bgcolor': "rgba(0,0,0,0)",
                         'xaxis': {
                             "title": x_title,
                             "showgrid": False,
                         },
                         'yaxis': {
                             "title": y_title,
                             "showgrid": False,
                             "range": [0, 0 if len(y) == 0 else max(y) * 1.1],
                         },
                         'margin': {"l": 0, "r": 0, "t": 0, "b": 0}
                     })


def calculate_periods_amount(start, end, length):
    """
    Calculates the amount of periods between two dates
    :param start: start date
    :param end: end date
    :param length: the length of each period
    :return: the amount of periods
    """
    start = datetime.datetime.strptime(start[:10], '%Y-%m-%d')
    end = datetime.datetime.strptime(end[:10], '%Y-%m-%d')
    return (end - start).days // length


def get_screen(i, period, start, end, location, strategy):
    """
    The function returns the screen according to the current index
    :param i: the current index
    :param period: the period length
    :param start: the start date
    :param end: the end date
    :param location: the location
    :param strategy: the strategy
    :return: the screen
    """
    # First screen - choose a city
    if i == 0:
        town_select = dcc.Dropdown(id="select",
                                   placeholder="Select a city",
                                   options=[{"label": city, "value": f"{loc[0]}/{loc[1]}/{city}"} for (city, loc) in
                                            df_objects.get_town_loc_by_name()], persistence=True,
                                   persistence_type='local', value="32.08/34.78/Tel Aviv-Yafo")
        return html.Div([dbc.Row([dbc.Col(html.H2("Choose a city"))]),
                         dbc.Row([dbc.Col(html.H1(" "))]),
                         dbc.Row([dbc.Col(town_select)]),
                        dbc.Row([dbc.Col(html.H1(" "))]),
                        dbc.Row([dbc.Col(html.H6(
                            "Select the city you want to simulate. We use this in order to get the solar radiation data for the simulation.",
                        style={"color": "rgb(40, 40, 40)"}))])],
                        style={"padding": "20px"})
    # Second screen - choose a date range
    if i == 1:
        return html.Div([dbc.Row([dbc.Col(html.H2("Choose a date range"))]),
                         dbc.Row([dbc.Col(html.H1(" "))]),
                         dbc.Row([dbc.Col(dcc.DatePickerRange(id="range-pick",
                                                              min_date_allowed=datetime.date(2017, 1, 1),
                                                              start_date=start,
                                                              end_date=end,
                                                              display_format="DD/MM/YYYY",
                                                              max_date_allowed=datetime.date(2050, 1, 1)))]),
                        dbc.Row([dbc.Col(html.H1(" "))]),
                         dbc.Row([dbc.Col(html.H6("Select the range of date you want to simulate. Notice that the simulation works only for dates between 2017 and 2050.",
                                                  style={"color": "rgb(40, 40, 40)"}))]),
                         ],
                        style={"padding": "20px"})
    # Third screen - choose a period length
    if i == 2:
        return html.Div([dbc.Row([dbc.Col(html.H2("Choose period length"))]),
                         dbc.Row([dbc.Col(html.H1(" "))]),
                         dbc.Row([dbc.Col(dbc.InputGroup(
                             [
                                 dbc.DropdownMenu(label='Units',
                                                  children=[dbc.DropdownMenuItem("days", id="days"),
                                                            dbc.DropdownMenuItem("months", id="months"),
                                                            dbc.DropdownMenuItem("years", id="years")],
                                                  id="units_select"),
                                 dbc.Input(id="input", type="number", min=1,
                                           step=1, value=period),
                                 dbc.InputGroupText("days", id="units")
                             ]
                         ))]),
                         dbc.Row([dbc.Col(html.H1(" "))]),
                         dbc.Row([dbc.Col(html.H6("Select the length of each period. Period is the time between purchase of new solar panels and baterries.", style={"color": "rgb(40, 40, 40)"}))]),
                         ],
                        style={"padding": "20px"})
    # Fourth screen - choose a purchase strategy
    if i == 3:
        return html.Div([dbc.Row([dbc.Col(html.H2("Enter purchase strategy"))]),
                         dbc.Row([dbc.Col(html.Div(style={"height": "16px"}))]),
                         dbc.Row(dbc.Row(
                             [dbc.Col([dbc.Button(children=DashIconify(icon="lucide:download", height=40), id="download", color="secondary"),
                                       dcc.Download(id="download-template")], width=1),
                              dbc.Col(dcc.Upload(
                                 id='upload-data',
                                 children=html.Div(
                                     dbc.Alert(html.Div(['Drag and Drop or ',
                                                         html.B('Select Files')],
                                                        style={"vertical-align": "center"}), id="msg",
                                               color="light"), style={"height": "40px"})
                                 ,
                                 style={
                                     'width': '100%',
                                     'height': '96px',
                                     'lineHeight': '60px',
                                     'borderWidth': '1px',
                                     'borderStyle': 'dashed',
                                     'borderRadius': '5px',
                                     'textAlign': 'center',
                                 },
                                 multiple=False
                             ))])),
                         dbc.Row([dbc.Col(html.Div(style={"height": "16px"}))]),
                         dbc.Row(dbc.Row([dbc.Col(dcc.Graph('myFig',
                                                            config={
                                                                "displayModeBar": False,
                                                                "scrollZoom": False,
                                                                "doubleClick": False,
                                                                "showTips": False
                                                            },
                                                            style={"height": "25vh"}), width=6),
                                          dbc.Col(dcc.Graph('myFig2',
                                                            config={
                                                                "displayModeBar": False,
                                                                "scrollZoom": False,
                                                                "doubleClick": False,
                                                                "showTips": False
                                                            },
                                                            style={"height": "25vh"}), width=6)]),
                                 id="graph-id"),
                         ],
                        style={"padding": "20px"})
    # Fifth screen - run the simulation
    if i == 4:
        location = location.split("/")
        return html.Div([dbc.Row([dbc.Col(html.H2("Run the simulation"))]),
                         dbc.Row([dbc.Col(html.P("\n\n\n"))]),
                         dbc.Row([dbc.Col(html.H4(html.I(className="bi bi-calendar3-range")), width=1),
                                  dbc.Col(f"{start} - {end}"),
                                  dbc.Col(html.H4(html.I(className="bi bi-hourglass-split")), width=1),
                                  dbc.Col(f"{period} days")]),
                         dbc.Row(
                             [dbc.Col(html.H4(html.I(className="bi bi-geo-alt-fill")), width=1),
                              dbc.Col(f"{location[2]}"),
                              dbc.Col(html.H4(html.I(className="bi bi-pin-map-fill")), width=1),
                              dbc.Col(f"{location[0]}/{location[1]}")]),
                         dbc.Row([dbc.Col(html.P("\n\n\n"))]),
                         dbc.Row([dbc.Col(dbc.Button("Run", id="run1", href="/display-result"))]),
                         html.Div(id="initial")
                         ],
                        style={"padding": "20px"})


center = {"position": "absolute", "top": "50%", "-ms-transform": "translateY(-50%)", "transform": "translateY(-50%)"}
bottom = {"position": "absolute", "top": "95%", "-ms-transform": "translateY(-50%)", "transform": "translateY(-50%)"}

layout = html.Div([dbc.Card(
    [dbc.CardBody([html.Div([dbc.Row([
        dbc.Col(html.Div(dbc.Button(DashIconify(icon="fluent-mdl2:back",
                                                height=40, color="rgba(50,50,50,0.5)"),
                                    id="prev", n_clicks=0, outline=False,
                                    color="transparent"),
                         className="text-center", style=center)),
        dbc.Col(dbc.Form(id="content"), width=10),
        dbc.Col(html.Div(dbc.Button(DashIconify(icon="fluent-mdl2:forward",
                                                height=40, color="rgba(50,50,50,0.5)"),
                                    id="next", n_clicks=0, outline=False,
                                    color="transparent"),
                         className="text-center", style=center))
    ],
        className="d-flex flex-wrap justify-content-center"),
        dbc.Row(dbc.Col(html.Small("1/5", style=bottom, id="step_num"), width=2),
                justify="center")])])]
    , style={"display": "block",
             "width": "70%",
             "padding": "10px",
             "margin": "5% 10% 15% 15%",
             "backdrop-filter": "blur(8px)"
             }, color="rgba(255, 255, 255, 0.3")
    , dcc.Store(id="city-lon-lat", storage_type='local', data=ConfigGetter['LOCATION'])
    , dcc.Store(id="date-start", storage_type='local',
                data=datetime.datetime.strptime(ConfigGetter['START_DATE'], ConfigGetter['TIME_FORMAT']))
    , dcc.Store(id="date-end", storage_type='local',
                data=datetime.datetime.strptime(ConfigGetter['END_DATE'], ConfigGetter['TIME_FORMAT']))
    , dcc.Store(id="period-length", storage_type='local', data=ConfigGetter['PERIODS_DAYS_AMOUNT'])
    , dcc.Store(id="purchase-strategy", storage_type='local', data=ConfigGetter['STRATEGY'])])


@callback(
    Output('content', 'children'),
    Output('prev', 'disabled'),
    Output('next', 'disabled'),
    Output('step_num', 'children'),
    Input('next', 'n_clicks'),
    Input('prev', 'n_clicks'),
    State("period-length", "data"),
    State("date-start", "data"), State("date-end", "data"),
    State('city-lon-lat', 'data'),
    State('purchase-strategy', 'data')
)
def update_output(n_clicks1, n_clicks2, period, start, end, loc, strategy):
    """
    Update the content of the page
    :param n_clicks1: next button clicks
    :param n_clicks2: prev button clicks
    :param period: period length
    :param start: start date
    :param end: end date
    :param loc: location
    :param strategy: purchase strategy
    :return: the content of the page
    """
    return get_screen(n_clicks1 - n_clicks2, period, start, end, loc,
                      strategy), n_clicks1 - n_clicks2 == 0 or n_clicks1 - n_clicks2 == 3, n_clicks1 - n_clicks2 == 4, f"{n_clicks1 - n_clicks2 + 1}/5"


@callback(
    Output('config', 'data'),
    Input('initial', 'children'),
    State("period-length", "data"),
    State("date-start", "data"), State("date-end", "data"),
    State('city-lon-lat', 'data'),
    State('purchase-strategy', 'data')
)
def update_config(n, period, start, end, loc, strategy):
    """
    Update the config file
    :param n: useless
    :param period: period length
    :param start: start date
    :param end: end date
    :param loc: location
    :param strategy: purchase strategy
    :return: the config file
    """
    with open("config.json") as json_file:
        config = json.load(json_file)

    config["TIME_FORMAT"] = '%Y-%m-%d'
    config["START_DATE"] = start
    config["END_DATE"] = end
    config["START_YEAR"] = int(start[:4])
    config["END_YEAR"] = int(end[:4])
    config["PERIODS_DAYS_AMOUNT"] = period
    config['STRATEGY'] = json.loads(strategy)
    loc = loc.split("/")
    config["LOCATION"] = {"latitude": float(loc[0]), "longitude": float(loc[1]), "name": loc[2]}

    return config


@callback(
    Output("period-length", "data"),
    Output("units", "children"),
    Input("months", "n_clicks"),
    Input("days", "n_clicks"),
    Input("years", "n_clicks"),
    Input("input", "value"),
    State("units", "children")
)
def select_unit(n1, n2, n3, length, prev):
    """
    Select the unit of the period
    :param n1: months button clicks
    :param n2: days button clicks
    :param n3: years button clicks
    :param length: input value
    :param prev: previous unit
    :return: the period length and the unit
    """
    if length is None:
        return ConfigGetter["PERIODS_DAYS_AMOUNT"], prev
    days = {"years": 365, "months": 30, "days": 1}
    ctx = dash.callback_context
    if not ctx.triggered or "input" in ctx.triggered[0]["prop_id"]:
        chosen = prev
    else:
        chosen = ctx.triggered[0]["prop_id"].split(".")[0]
    return length * days[chosen], chosen


@callback(Output("date-start", "data"), Output("date-end", "data"),
          Input('range-pick', 'start_date'),
          Input('range-pick', 'end_date')
          )
def change_date(start, end):
    """
    Update the start and end dates
    :param start: start date
    :param end: end date
    :return: the start and end dates
    """
    return start[:10], end[:10]


@callback(
    Output('city-lon-lat', 'data'),
    Input('select', 'value'),
    prevent_initial_call=True
)
def update_output(value):
    """
    Update the location
    :param value: location
    :return: the location
    """
    return value


@callback(
    Output('download-template', 'data'),
    Input('download', 'n_clicks'),
    State('period-length', 'data'),
    State("date-start", "data"), State("date-end", "data"),
    prevent_initial_call=True
)
def update_output(n, length, start, end):
    """
    Update the template file
    :param n: download button clicks
    :param length: period length
    :param start: start date
    :param end: end date
    :return: the template file
    """
    period_amount = calculate_periods_amount(start, end, length)
    df = {'period': [i + 1 for i in range(period_amount)], 'solar_panel_purchased': [0] * period_amount,
          'batteries_purchased': [0] * period_amount}
    df = pandas.DataFrame(data=df)
    return dcc.send_data_frame(df.to_csv, "template.csv", index=False)


@callback(
    Output('purchase-strategy', 'data'),
    Output('msg', 'children'),
    Output('msg', 'color'),
    Output('myFig', 'figure'),
    Output('myFig2', 'figure'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State("date-start", "data"),
    State("date-end", "data"),
    State('period-length', 'data')
)
def update_output(content, file_name, start, end, length):
    """
    Update the purchase strategy
    :param content: file content
    :param file_name: file name
    :param start: start date
    :param end: end date
    :param length: period length
    :return: the purchase strategy
    """
    result = [None, None, None]
    x = []
    y = [[], []]
    if content is not None:
        try:
            if file_name.split('.')[1] != 'csv':
                raise Exception("Bad file type")
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            df = pd.read_csv(io.BytesIO(decoded), header=[0])
            if len(df.columns) != 3 \
                    or not numpy.array_equal(df.columns.to_numpy(),
                                             numpy.array(['period', 'solar_panel_purchased', 'batteries_purchased'])) \
                    or df.count()[0] != calculate_periods_amount(start, end, length) \
                    or not all(str(x).isnumeric() for x in df['solar_panel_purchased']) \
                    or not all(str(x).isnumeric() for x in df['batteries_purchased']):
                raise Exception("Bad file format")
            result[1], result[2] = "Success!", "success"
            result[0] = df
            x = df["period"]
            y = [df["solar_panel_purchased"], df["batteries_purchased"]]
        except Exception as e:
            result[1], result[2] = str(e) + ". Try again!", "danger"
            result[0] = None
    else:
        result[1], result[2] = html.Div(['Drag and Drop or ', html.B('Select Files')]), "light"

    if result[0] is None:
        period_amount = calculate_periods_amount(start, end, length)
        result[0] = pandas.DataFrame(
            data={'period': [i + 1 for i in range(period_amount)], 'solar_panel_purchased': [1300] * period_amount,
                  'batteries_purchased': [100000] * period_amount})
        x = [i + 1 for i in range(period_amount)]
        y = [[1300] * period_amount, [100000] * period_amount]

    fig = get_strategy_graph(x, y[0], "Power [kW]", "period")
    fig2 = get_strategy_graph(x, y[1], "Capacity [kWh]", "period")

    return result[0][['solar_panel_purchased', 'batteries_purchased']].to_json(), result[1], result[2], fig, fig2
