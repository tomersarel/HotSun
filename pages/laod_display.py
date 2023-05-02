import itertools

from imports import *
from df_objects import *
import pandas as pd
import numpy as np

FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css", FONT_AWESOME]

roundbutton = {
    "border": "2px solid grey",
    "border-radius": "50%",
    "padding": 0,
    "background-color": "transparent",
    "color": "black",
    "text-align": "center",
    "display": "inline-block",
    "font-size": 16,
    "height": 25,
    "width": 25,
    "margin": 0,
}

energy_columns = ['Batteries', 'Solar', 'Buying', 'Selling', 'Lost', 'Storaged']
pollution_columns = ['periodic_C02', 'periodic_SOx', 'periodic_PMx']
colors = {"Solar": "#ffe205", "Batteries": "#d4d4d4", "Buying": "#ec4141", "Selling": "#5fbb4e", "Storaged": "#9edbf9",
          "Lost": "gray", 'periodic_C02': "red", 'periodic_SOx': "blue", 'periodic_PMx': "gray"}


def generate_energy_graph_by_date_range(start, end, df, resample='H'):
    """
    generate energy graph by Datetime.Datetime range and resample it.
    :param start: the start date
    :param end: the end date
    :param df: the energy df
    :param resample: the resample type
    :return: array of bars by different energy types
    """
    # df = df.set_index(['Date'])
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


def calculus(config, df_energy):
    # calculate solar energy percentage
    df_energy['Total'] = df_energy['Solar'] + df_energy['Buying'] + df_energy['Batteries']
    
    total_energy = df_energy['Total'].sum()
    solar_energy = df_energy['Solar'].sum()
    solar_percentage = round((solar_energy / total_energy) * 100, 2)

    # calculate CO2 pollution saved
    co2_saved = round((solar_energy * 0.0004), 2)

    solar_energy_production = df_energy['Solar'].mean()
    electricity_rate = 0.068  # Replace 0.15 with your electricity rate in dollars per kWh
    israel_produs_power_solar = 1438000
    impact = (df_energy['Solar'].mean() / israel_produs_power_solar).__round__(5)
    savings = (solar_energy_production * electricity_rate).__round__(1)
    # Calculate the impact increase
    years_in_period = 10
    zion = sum((df_energy['Solar'].mean() * (1 + 0.05) ** np.arange(0,
                                                                    years_in_period)) / israel_produs_power_solar).__round__(
        5)
    impact_increase = (zion / impact).__round__(0)

    # create a dictionary with all the calculated values
    results = {
        'solar_percentage': solar_percentage,
        'co2_saved': co2_saved,
        'savings': savings,
        'impact': impact,
        'impact_increase': impact_increase,

    }

    return results


def grade(calculus_results):
    green_g = 0
    solar_percentage = calculus_results['solar_percentage']

    if solar_percentage < 0:
        green_g += 5
    elif 10 <= solar_percentage < 20:
        green_g += 15
    elif 30 <= solar_percentage < 45:
        green_g += 25
    else:
        green_g += 30
    impact =  calculus_results['impact']
    if (calculus_results['impact'] > 0.0001):
        green_g += 2
    elif impact > 0.001 :
        green_g += 4
    elif impact > 0.01:
        green_g += 6
    elif impact > 0.1:
        green_g += 8
    elif impact > 0.5:
        green_g += 10
        co2_saved = calculus_results['co2_saved']
        if co2_saved < 100000:
            green_g += 5
        elif 100000 <= co2_saved < 500000:
            green_g += 10
        elif 500000 <= co2_saved < 1000000:
            green_g += 15
        else:
            green_g += 20
        savings_per_hour = calculus_results['savings']
        if savings_per_hour < 100:
            green_g += 10
        elif 10 <= savings_per_hour < 200:
            green_g += 20
        elif 30 <= savings_per_hour < 300:
            green_g += 30
        else:
            green_g += 40

    return green_g


def get_display(config, df_energy, df_finance):
    results = calculus(config, df_energy)
    green_g = grade(results)
    # create display summary
    display_summery = html.Div([
        html.Div([
            dbc.Card([
                dbc.CardBody([
                    html.H1(f"{results['solar_percentage']}%", className="card-title", style={"text-align": "center", "font-size": 48}),
                    html.H4("Solar Energy", className="card-title", style={"text-align": "center"}),
                    html.P(
                        "Percentage of solar energy out of total energy consumption.",
                        className="card-text",
                    )
                ])
            ], style={"width": "18rem"}, className="mx-2 my-2"),
            dbc.Card([
                dbc.CardBody([
                    html.H1(f"{results['co2_saved']} kg", className="card-title", style={"text-align": "center", "font-size": 48}),
                    html.H4("Pollution Saved", className="card-title", style={"text-align": "center"}),
                    html.P(
                        "Amount of CO2 pollution saved by producing energy by using solar panels.",
                        className="card-text",
                    )
                ])
            ], style={"width": "18rem"}, className="mx-2 my-2"),
            dbc.Card([
                dbc.CardBody([
                    html.H1(f"{results['savings']}$", className="card-title", style={"text-align": "center", "font-size": 48}),
                    html.H4("Finance", className="card-title", style={"text-align": "center"}),
                    html.P(
                        ('this is how much you have saved by a avarage hour'),
                        className="card-text",
                    )
                ])
            ], style={"width": "18rem"}, className="mx-2 my-2"),
            dbc.Card([
                dbc.CardBody([
                    html.H1(f"{results['impact']}%", className="card-title", style={"text-align": "center", "font-size": 48}),
                    html.H4("Climate Change", className="card-title", style={"text-align": "center"}),
                    html.P(
                        "this is your Percenteg of the israel production power of solar energy",
                        className="card-text",
                    )
                ])
            ], style={"width": "18rem"}, className="mx-2 my-2"),
            dbc.Card([
                dbc.CardBody([
                    html.H1(f"{results['impact_increase']}X", className="card-title", style={"text-align": "center", "font-size": 48}),
                    html.H4("incrise in impact", className="card-title", style={"text-align": "center"}),
                    html.P(
                        ('this is how much will be your procenteg out of tatal israel produs power of solar energy will multiplay if you increase by 5% your prous every year for 10 years '),
                        className="card-text",
                    )
                ])
            ], style={"width": "18rem"}, className="mx-2 my-2"),
            dbc.Card([
                dbc.CardBody([
                    html.H1(f"{green_g}/100",  className="card-title",
                            style={"text-align": "center", "font-size": 48}),
                    html.H4("incrise in impact", className="card-title", style={"text-align": "center"}),
                    html.P(
                        (
                            'this is your green grade '),
                        className="card-text",
                    )
                ])
            ], style={"width": "18rem"}, className="mx-2 my-2"),
        ], className="d-flex flex-wrap justify-content-center"),
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
                                                data=[go.Bar(x=df_finance.index, y=df_finance[col], name=col,
                                                             marker={'color': colors[col], 'line.width': 0})
                                                      for index, col in enumerate(pollution_columns)],
                                                layout=go.Layout(title=f"total pollution per period")),

                                            style={"height": "600px"})])

    display = html.Div([dbc.Accordion([dbc.AccordionItem(display_summery, title='Summery'),
                                       dbc.AccordionItem(display_energy, title='Energy'),
                                       dbc.AccordionItem(display_finance, title='Finance'),
                                       dbc.AccordionItem(display_pollution, title='Pollution')],
                                      always_open=True),

                        ], style={"overflow": "auto", "height": "90vh", "background": "rgba(255, 255, 255, 0.3)",
                                  "backdrop-filter": "blur(8px)",
                                  "border-radius": "10px"})
    return display

def create_list(units_dict, units, explain):
    """
    Create a list of all the values by order from recursive dict
    """
    for key, val in units_dict.items():
        if isinstance(val, dict):
            units, explain = create_list(val, units, explain)
        else:
            units.append(val.pop(0))
            explain.append(val.pop(0))

    return units, explain


def get_parameters(config, units, explain, id=itertools.count(), loc=""):
    result = []

    for parameter, value in config.items():
        if parameter not in ConfigGetter.private_keys:
            parameter_name = parameter.replace("_", " ").lower().capitalize()
            if type(value) in {int, float}:
                if parameter.isnumeric():
                    result.append(dbc.Row([
                        dbc.Col([f"Period {int(parameter) + 1}:"], width="auto"),
                        dbc.Col(
                        dbc.Input(
                            id={'type': 'config-input', 'index': id.__next__()},
                            value=f"{value}",
                            type="number"
                        ), width=True)
                    ], className="my-2", align="center"))
                else:
                    result.append(dbc.Row([
                        dbc.Col([f"{parameter_name}:"], width="auto"),
                        dbc.Col([dbc.Button("?", id=f"{loc}-{parameter}", className="fa-question-circle",
                                            style=roundbutton),
                                 dbc.Popover(explain.pop(0), body=True, target=f"{loc}-{parameter}",
                                             trigger="hover", placement="right-start")], width=2),
                        dbc.Col(
                            dbc.InputGroup(
                                [
                                    dbc.Input(
                                        id={'type': 'config-input', 'index': id.__next__()},
                                        value=f"{value}",
                                        type="number"
                                    ),
                                    dbc.InputGroupText(units.pop(0)),
                                ]
                            )
                            , width=True)
                    ], className="my-2", align="center"
                    ))
            elif type(value) == dict:
                result.append(dbc.Row(
                    dbc.Accordion(dbc.AccordionItem(get_parameters(value, units, explain, id, f"{loc}-{parameter}"),
                                                    title=parameter_name),
                                  start_collapsed=True)
                ))

    return result


def get_parameter_wrapper(config):
    with open(ConfigGetter.units_path) as f:
        units_data = json.load(f)
    units, explain = create_list(units_data, [], [])
    return get_parameters(config, units, explain)

