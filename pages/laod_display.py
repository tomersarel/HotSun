from imports import *
from df_objects import *
import pandas as pd
import numpy as np

energy_columns = ['Batteries', 'Solar', 'Buying', 'Selling', 'Lost', 'Storaged']
colors = {"Solar": "#ffe205", "Batteries": "#d4d4d4", "Buying": "#ec4141", "Selling": "#5fbb4e", "Storaged": "#9edbf9",
          "Lost": "gray"}


def generate_year_enr_graph(start_year, end_year, df, resample='D'):
    data = df[(df['Date'] >= datetime.datetime(year=start_year, day=1, month=1)) & (
            df['Date'] < datetime.datetime(year=end_year, day=1, month=1))]
    data = data.resample(resample, on='Date', convention="start").sum()
    return [go.Bar(x=data.index, y=data[col], name=col, marker={'color': colors[col], 'line.width': 0}) for col in
            energy_columns]


def generate_day_enr_graph(date, df):
    df = df[(df['Date'] >= date) & (df['Date'] < date + datetime.timedelta(days=1))]
    df = df.set_index('Date')
    return [go.Bar(x=df.index.hour, y=df[col], name=col, marker={'color': colors[col], 'line.width': 0}) for col in
            energy_columns]


def dict_to_dataframe(df):
    df = pd.DataFrame(df)
    if df.empty:
        return df
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df.set_index('Date')
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
    if (calculus_results['solar_percentage'] > 10):
        green_g += 30
    if (calculus_results['impact'] > 0.0001):
        green_g += 10
    if (calculus_results['co2_saved'] > 50):
        green_g += 20
    if (calculus_results['savings'] > 200):
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
                        "Amount of CO2 pollution saved by producing solar energy.",
                        className="card-text",
                    )
                ])
            ], style={"width": "18rem"}, className="mx-2 my-2"),
            dbc.Card([
                dbc.CardBody([
                    html.H1(f"{results['savings']} $", className="card-title", style={"text-align": "center", "font-size": 48}),
                    html.H4("Finance", className="card-title", style={"text-align": "center"}),
                    html.P(
                        ('this is how much you have saved by avarage period'),
                        className="card-text",
                    )
                ])
            ], style={"width": "18rem"}, className="mx-2 my-2"),
            dbc.Card([
                dbc.CardBody([
                    html.H1(f"{results['impact']} $", className="card-title", style={"text-align": "center", "font-size": 48}),
                    html.H4("Climate Change", className="card-title", style={"text-align": "center"}),
                    html.P(
                        "this is your procenteg of the israel produs power of solar energy",
                        className="card-text",
                    )
                ])
            ], style={"width": "18rem"}, className="mx-2 my-2"),
            dbc.Card([
                dbc.CardBody([
                    html.H1(f"{results['impact_increase']} X", className="card-title", style={"text-align": "center", "font-size": 48}),
                    html.H4("incrise in impact", className="card-title", style={"text-align": "center"}),
                    html.P(
                        ('this is how much will be your procenteg out of tatal israel produs power of solar energy will multiplay if you increase by 5% your prous every year '),
                        className="card-text",
                    )
                ])
            ], style={"width": "18rem"}, className="mx-2 my-2"),
            dbc.Card([
                dbc.CardBody([
                    html.H1(f"{green_g} /100",  className="card-title",
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

def get_parameters(config):
    result = []
    for parameter, value in config.items():
        if parameter not in ["START_YEAR", "END_YEAR", "PERIODS_DAYS_AMOUNT"]:
            parameter = parameter.replace("_", " ").lower().capitalize()
            if type(value) == int:
                result.append(dbc.Row(
                    [dbc.Col(f"{parameter}:", width="auto"), dbc.Col(dbc.Input(placeholder=f"{value}", type="number"))],
                    className="my-2"))
            elif type(value) == dict:
                result.append(dbc.Row(
                    dbc.Accordion(dbc.AccordionItem(get_parameters(value), title=parameter), start_collapsed=True)))
    return result