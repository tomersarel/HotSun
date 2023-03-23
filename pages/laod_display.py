from imports import *
from df_objects import *


energy_columns = ['Batteries', 'Solar', 'Buying', 'Selling', 'Lost', 'Storaged']
colors = {"Solar": "#ffe205", "Batteries": "#d4d4d4", "Buying": "#ec4141", "Selling": "#5fbb4e", "Storaged": "#9edbf9",
          "Lost": "gray"}


def generate_energy_graph_by_date_range(start, end, df, resample='H'):
    """
    generate energy graph by Datetime.Datetime range and resample it.
    :param start: the start date
    :param end: the end date
    :param df: the energy df
    :param resample: the resample type
    :return: array of bars by different energy types
    """
    #df = df.set_index(['Date'])
    data = df[(df.index >= start) & (df.index < end)]
    if resample != 'H':
        data = data.resample(resample, convention="start").sum()
    return [go.Bar(x=data.index, y=data[col], name=col, marker={'color': colors[col], 'line.width': 0}) for col in
            energy_columns]


def generate_year_enr_graph(start_year, end_year, df, resample='Y'):
    """
    generate energy graph by year range and resample it
    """
    return generate_energy_graph_by_date_range(datetime.datetime(year=start_year, day=1, month=1),
                                               datetime.datetime(year=end_year, day=1, month=1),
                                               df, resample)


def generate_day_enr_graph(date, df):
    """
        generate energy graph for single date by hour
    """
    return generate_energy_graph_by_date_range(date,
                                               date + datetime.timedelta(days=1),
                                               df, 'H')


def dict_to_dataframe(df):
    """
    this function create data frame from dict
    :param df: the given dict
    :return: pandas data frame
    """
    df = pd.DataFrame(df)
    if df.empty:
        return df
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df = df.set_index('Date')
    for coloumn in df.columns:
        if coloumn in energy_columns:
            df[coloumn] = pd.to_numeric(df[coloumn])
    return df


def get_display(config, df_energy, df_finance):
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
            data=generate_year_enr_graph(config['START_YEAR'], config['END_YEAR'], dict_to_dataframe(df_energy), 'Y'),
            layout=go.Layout(barmode='stack', title=f"yearly energy distribution")))
    ])
    display_energy = html.Div([dcc.Slider(id="period_slider",
                                          min=config["START_YEAR"],
                                          max=config["END_YEAR"] - 1,
                                          step=1,
                                          marks={i: '{}'.format(i) for i in
                                                 range(config["START_YEAR"], config["END_YEAR"] - 1)},
                                          value=config["START_YEAR"]),
                               dcc.Graph(id='yearlyEnergyGraph'),
                               dcc.Graph(id='dailyGraph', style={"display": "None"})
                               ])
    df_finance = pd.DataFrame(df_finance)
    display_finance = html.Div([dcc.Graph(id='yearlyCostGraph',
                                          figure=go.Figure(
                                              data=go.Bar(x=df_finance.index, y=df_finance['periodic_cost'],
                                                          name='cost', marker={'color': 'green', 'line.width': 0}),
                                              layout=go.Layout(barmode='stack', title=f"total cost per period")),
                                          ),
                                dcc.Graph(id='yearlyProfitGraph',
                                          figure=go.Figure(
                                              data=go.Bar(x=df_finance.index, y=df_finance['periodic_profit'],
                                                          name='cost', marker={'color': 'green', 'line.width': 0}),
                                              layout=go.Layout(barmode='stack', title=f"total profit per period")),
                                          )
                                ])

    display_pollution = html.Div([dcc.Graph(id='yearlyPollutionGraph',
                                            figure=go.Figure(
                                                data=go.Bar(x=df_finance.index, y=df_finance['periodic_pollute'],
                                                            name='cost', marker={'color': 'red', 'line.width': 0}),
                                                layout=go.Layout(barmode='stack', title=f"total pollution per period")),
                                            style={"height": "600px"})])

    display = html.Div([dbc.Accordion([dbc.AccordionItem(display_summery, title='Summery'),
                                       dbc.AccordionItem(display_energy, title='Energy'),
                                       dbc.AccordionItem(display_finance, title='Finance'),
                                       dbc.AccordionItem(display_pollution, title='Pollution')],
                                      always_open=True),

                        ], style={"overflow": "auto", "height": "92vh"})
    return display



def get_parameters(config, n=0):
    result = []
    for i, (parameter, value) in enumerate(config.items()):
        if parameter not in ["START_YEAR", "END_YEAR", "PERIODS_DAYS_AMOUNT"]:
            parameter = parameter.replace("_", " ").lower().capitalize()
            if type(value) == int:
                result.append(dbc.Row(
                    [dbc.Col(f"{parameter}:", width="auto"), dbc.Col(dbc.Input(id={'type': 'config-input', 'index': i},
                                                                               value=f"{value}", type="number"))],
                    className="my-2"))
            elif type(value) == dict:
                result.append(dbc.Row(
                    dbc.Accordion(dbc.AccordionItem(get_parameters(value, n+i), title=parameter), start_collapsed=True)))
    return result

