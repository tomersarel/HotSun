import itertools

from imports import *
from df_objects import *
import pandas as pd
import numpy as np

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
energy_columns = ['Batteries', 'Solar', 'Buying', 'Selling', 'Lost', 'Stored']
pollution_columns_greenhouse_gases = ['periodic_C02']
pollution_columns_other = ['periodic_SOx', 'periodic_PMx']
cost_columns = ['buying_electricity_cost',
                'periodic_batteries_capex_cost', 'periodic_batteries_opex_cost',
                'periodic_panels_capex_cost', 'periodic_panels_opex_cost']
profit_columns = ['periodic_selling_profit', 'periodic_didnt_buy']
colors = {"Solar": "#ffe205", "Batteries": "#d4d4d4", "Buying": "#ec4141", "Selling": "#5fbb4e", "Stored": "#9edbf9",
          "Lost": "gray", 'periodic_C02': "red", 'periodic_SOx': "blue", 'periodic_PMx': "gray"}


def get_figure(data, title_label, x_axis_label, y_axis_label, bar_mode='stack', bargap=None):
    """
    generate a figure with the given data
    :param data: the data to be displayed (go object)
    :param title_label: the title of the graph
    :param x_axis_label: the x-axis label
    :param y_axis_label: the y-axis label
    :param bar_mode: the bar mode
    :param bargap: the bar gap
    :return: the figure
    """
    return go.Figure(data=data,
                     layout=go.Layout(barmode=bar_mode,
                                      title={
                                          'text': title_label,
                                          'font': {'size': 20},
                                          'x': 0.5
                                      },
                                      bargap=bargap,
                                      xaxis={"title": x_axis_label,
                                             "showspikes": False,
                                             },
                                      yaxis={"title": y_axis_label}),
                     )


def generate_energy_graph_by_date_range(start, end, df, resample='H'):
    """
    generate energy graph by Datetime.Datetime range and resample it.
    :param start: the start date
    :param end: the end date
    :param df: the energy df
    :param resample: the resample type
    :return: array of bars by different energy types
    """
    data = df[(df.index >= start) & (df.index < end)]
    if resample != 'H':
        data = data.resample(resample, convention="start").sum()
    return [go.Bar(x=data.index, y=data[col], name=col, marker={'color': colors[col], 'line.width': 0}) for col in
            energy_columns]


def generate_energy_graph_by_year_range(start_year, end_year, df, resample='Y'):
    """
    generate energy graph by year range and resample it.
    :param start_year: the start year
    :param end_year: the end year
    :param df: the energy df
    :param resample: the resample type
    :return: array of bars by different energy types
    """
    return generate_energy_graph_by_date_range(datetime.datetime(year=start_year, day=1, month=1),
                                               datetime.datetime(year=end_year, day=1, month=1),
                                               df, resample)


def generate_daily_energy_graph_by_date(date, df):
    """
    generate daily energy graph by date
    :param date: the date
    :param df: the energy df
    :return: array of bars by different energy types
    """
    return generate_energy_graph_by_date_range(date,
                                               date + datetime.timedelta(days=1),
                                               df, 'H')


def generate_yaerly_renewable_energy_precentage_graph(df_energy):
    """
    generate yearly renewable energy percentage graph
    :param df_energy: the energy df
    :return: the graph
    """
    yearly = df_energy.resample("Y", convention="start").sum()
    yearly['percentages'] = (yearly['Solar'] + yearly['Batteries']) / (
            yearly['Solar'] + yearly['Batteries'] + yearly['Buying']) * 100
    yerly_figure = get_figure(
        go.Scatter(x=yearly.index, y=yearly['percentages'], mode='lines', name='Solar Energy Percentage'),
        "Yearly Solar Energy Percentage",
        "Year",
        "Solar Energy Percentage [%]")

    # add lines to the graph to show the goals of the NZO, Israel and Tel-Aviv
    yerly_figure.update_layout(shapes=[
        go.layout.Shape(type='line', y0=95, x0=min(yearly.index), x1=max(yearly.index), y1=95,
                        line=dict(color='#808080', dash='dash')),
        go.layout.Shape(type='line', y0=30, x0=min(yearly.index), x1=max(yearly.index), y1=30,
                        line=dict(color='#808080', dash='dash'))
    ],
        yaxis=dict(range=[0, 100]),
        annotations=[
            go.layout.Annotation(
                x=yearly.index.min(), y=90, xanchor="left",
                text='NZO national goal for 2050',
                showarrow=False,
                font=dict(size=12, color='#808080')
            ),
            go.layout.Annotation(
                x=yearly.index.min(), y=25, xanchor="left",
                text='Israel national goal for 2030',
                showarrow=False,
                font=dict(size=12, color='#808080')
            )
        ]
    )

    return yerly_figure


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


def calculate_interesting_numbers(config, df_energy, df_finance):
    """
    this function calculate interesting numbers for the dashboard
    :param config: the config file
    :param df_energy: the energy data frame
    :param df_finance: the finance data frame
    :return: dictionary of interesting numbers and their values for the dashboard
    """
    # calculate solar energy percentage in last year
    df_energy['Total'] = df_energy['Solar'] + df_energy['Buying'] + df_energy['Batteries']
    last_year = df_energy[df_energy["Date"] >= df_energy["Date"].max() - pd.DateOffset(years=1)]
    total_energy = last_year['Total'].sum()
    green_energy_last_year = last_year['Solar'].sum() + last_year['Batteries'].sum()
    solar_percentage = round((green_energy_last_year / total_energy) * 100)

    green_energy = df_energy['Solar'].sum() + df_energy['Batteries'].sum()
    # calculate CO2 pollution saved
    co2_saved = round(green_energy * config["pollution_rates"]["CO2"] / 1e9, 2)

    savings = round(df_finance['periodic_didnt_buy'].sum() -
                    df_finance['periodic_batteries_capex_cost'].sum() -
                    df_finance['periodic_batteries_opex_cost'].sum() -
                    df_finance['periodic_panels_capex_cost'].sum() -
                    df_finance['periodic_panels_opex_cost'].sum())

    # create a dictionary with all the calculated values
    results = {
        'solar_percentage': [solar_percentage, "%", "Solar Energy",
                             "Renewable energy usage out of the total energy consumption in the last year of the scenario.",
                             "ic:outline-solar-power", "#808080"],
        'co2_saved': [co2_saved, "kt", "Pollution Saved",
                      "CO2 pollution saved by converting to solar energy.",
                      "mdi:molecule-co2", "#808080"],
        'savings': [savings, "₪", "Savings",
                    "Money saved by using solar energy, after taking into account the capex and the opex of the system.",
                    "fluent-mdl2:savings", "#808080"]
    }

    return results


def grade(grades, df_energy, df_finance):
    """
    this function calculate the grade of the senerio
    :param grades: the grades dictionary
    :param df_energy: the energy data frame
    :param df_finance: the finance data frame
    :return: the environmental grade, the financial grade and the total grade
    """
    profit = sum([df_finance[col].sum() for col in profit_columns])
    cost = sum([df_finance[col].sum() for col in cost_columns])
    balance = profit - cost
    financial = round((0.5 + 0.5 * (balance / profit if balance > 0 else balance / cost)) * 100)
    environmental = grades['solar_percentage'][0]
    return [environmental, round((environmental + financial) / 2), financial]


def get_score_display(score, label):
    """
    this function create the score display for the dashboard
    :param score: the score
    :param label: the label of the score
    :return: the score display
    """
    return html.Div([html.Div(dcc.Graph(
        figure=go.Figure(
            data=[go.Pie(labels=['', ''], values=[100 - score, score],
                         marker=dict(
                             colors=['#FFFFFF', ['#FF0000', '#FFA500', '#00FF00'][score // 34]]
                         ),
                         hoverinfo='none',
                         textinfo='none',
                         hole=.65,
                         showlegend=False,
                         sort=False
                         )],
            layout=go.Layout(annotations=[go.layout.Annotation(text=f"{score}%", showarrow=False,
                                                               font=dict(size=32, color='black'))],
                             margin=dict(t=0, b=1))
        ),
        config={
            "scrollZoom": False,
            "doubleClick": False,
            "displayModeBar": False,
            "showTips": False
        },
        style={"height": "200px", "width": "100%", "align-items": "center"}
        , className="d-flex flex-wrap justify-content-center"
    )), html.H4(label)], style={"text-align": "center"})


def get_card_display(value, unit, title, explanation, icon, color="black"):
    """
    this function create a card display for the dashboard
    :param value: the value of the card
    :param unit: the unit of the value
    :param title: the title of the card
    :param explanation: the explanation of the card
    :param icon: the icon of the card
    :param color: the color of the card
    :return: the card display
    """
    return dbc.Card([
        dbc.CardBody([
            html.H4(html.I(className=icon), className="card-title",
                    style={"text-align": "center", "font-size": 108, "color": color}),
            html.Div(DashIconify(icon=icon, color=color, width=108, height=108,
                                 style={"display": "flex", "justify-content": "center"}, className="card-title"),
                     className="d-flex align-items-center justify-content-center"),
            html.H1(f"{'{:,}'.format(value)} {unit}", className="card-title", style={"text-align": "center", "font-size": 48}),
            html.H4(title, className="card-title", style={"text-align": "center"}),
            html.P(explanation, className="card-text")
        ])], style={"width": "20rem"}, className="mx-2 my-2")


def get_display(config, df_energy, df_finance):
    """
    this function create the display of the dashboard
    :param config: the config file
    :param df_energy: the energy data frame
    :param df_finance: the finance data frame
    :return: the display of the dashboard by summery section, energy section, finance section and pollution section
    """
    results = calculate_interesting_numbers(config, df_energy, df_finance)
    grades = grade(results, df_energy, df_finance)
    df_energy = dict_to_dataframe(df_energy)
    df_finance = pd.DataFrame(df_finance)
    display_summery = html.Div([
        dbc.Row([dbc.Col(get_score_display(score, label), width=12 // len(grades), align="center") for score, label in
                 zip(grades, ['Environmental Score', 'Overall Score', 'Financial Score'])],
                className="d-flex flex-wrap justify-content-center", style={"margin-bottom": "20px"}),

        html.Div([get_card_display(*params) for params in results.values()
                  ], className="d-flex flex-wrap justify-content-center"),

        dcc.Graph(figure=get_figure(
            generate_energy_graph_by_year_range(config['START_YEAR'], config['END_YEAR'], df_energy, 'Y'),
            "Yearly total Energy Distribution",
            "Year",
            "Energy [kWh]"),
            config={"displayModeBar": False}),
        dcc.Graph(figure=generate_yaerly_renewable_energy_precentage_graph(df_energy),
                  config={"displayModeBar": False}),
        dcc.Graph(figure=get_figure(
            [go.Scatter(x=df_finance.index, y=df_finance["is_full"], mode='lines',
                        name=f"High Capacity Usage (>{config['warnings']['max_capacity_threshold']}%)"),
             go.Scatter(x=df_finance.index, y=df_finance["is_empty"], mode='lines',
                        name=f"Low Capacity Usage (<{config['warnings']['min_capacity_threshold']}%)")],
            f"Usage Profile of Batteries along the Periods",
            "Period",
            "Percentage of Days in the Period [%]"),
            config={"displayModeBar": False}) if np.any(df_finance["is_full"] != 0) or np.any(
            df_finance["is_empty"] != 0) else None,
        dbc.Alert(
            [
                html.B([html.I(className="bi bi-exclamation-circle-fill mr-2"), "  Warning!"]),
                f" In some periods the batteries are at very high capacity (>{config['warnings']['max_capacity_threshold']}%). Consider adding more storage in the purchase strategy."
            ],
            color="warning"
        )
        if np.any(df_finance["is_full"] != 0) else None,
        dbc.Alert(
            [
                html.B([html.I(className="bi bi-exclamation-circle-fill mr-2"), "  Warning!"]),
                f" In some periods the batteries are at very low capacity (<{config['warnings']['min_capacity_threshold']}%). Consider decrease amount of storage in the purchase strategy."
            ],
            color="warning"
        )
        if np.any(df_finance["is_empty"] != 0) else None
    ])
    display_energy = html.Div([dcc.Slider(id="period_slider",
                                          min=config["START_YEAR"],
                                          max=config["END_YEAR"] - 1,
                                          step=1,
                                          marks={i: '{}'.format(i) for i in
                                                 range(config["START_YEAR"], config["END_YEAR"] - 1)},
                                          value=config["START_YEAR"]),
                               dcc.Graph(id='yearlyEnergyGraph', config={"displayModeBar": False}),
                               dcc.Graph(id='dailyGraph', style={"display": "None"}, config={"displayModeBar": False})
                               ])
    display_finance = html.Div([dcc.Graph(id='yearlyCostGraph',
                                          figure=get_figure([go.Bar(x=df_finance.index, y=df_finance[col],
                                                                    name=col.replace('_', " ").title(),
                                                                    marker={'line.width': 0}) for col in cost_columns],
                                                            "Total Cost per Period",
                                                            "Period",
                                                            "Cost per Period [₪]"),
                                          config={"displayModeBar": False}),
                                dcc.Graph(id='yearlyProfitGraph',
                                          figure=get_figure([go.Bar(x=df_finance.index, y=df_finance[col],
                                                                    name=col.replace('_', " ").title(),
                                                                    marker={'line.width': 0}) for col in
                                                             profit_columns],
                                                            "Total Profit per Period",
                                                            "Period",
                                                            "Profit per Period [₪]"),
                                          config={"displayModeBar": False})
                                ])

    display_pollution = html.Div([dcc.Graph(id='yearlyPollutionGraph',
                                            figure=get_figure(
                                                [go.Bar(x=df_finance.index, y=df_finance[col], name=col.replace('_', " ").title(),
                                                        marker={'color': colors[col], 'line.width': 0})
                                                 for index, col in enumerate(pollution_columns_greenhouse_gases)],
                                                "CO2 Pollutes per Period",
                                                "Period",
                                                "Pollutes [kg]",
                                                bar_mode="group"
                                            ),
                                            config={"displayModeBar": False}),
                                  dcc.Graph(id='yearlyPollutionGraph',
                                            figure=get_figure(
                                                [go.Bar(x=df_finance.index, y=df_finance[col], name=col.replace('_', " ").title(),
                                                        marker={'color': colors[col], 'line.width': 0})
                                                 for index, col in enumerate(pollution_columns_other)],
                                                "Other Gases Pollutes per Period",
                                                "Period",
                                                "Pollutes [kg]",
                                                bar_mode="group"
                                            ),
                                            config={"displayModeBar": False})
                                  ])

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
    Creates a list of units and explanations from a dictionary
    :param units_dict: dictionary of units and explanations
    :param units: list of units
    :param explain: list of explanations
    :return: units, explain
    """
    for key, val in units_dict.items():
        if isinstance(val, dict):
            units, explain = create_list(val, units, explain)
        else:
            units.append(val.pop(0))
            explain.append(val.pop(0))

    return units, explain


def get_parameters(config, units, explain, id=itertools.count(), loc=""):
    """
    Creates controls for the user to change the parameters of the senerio
    :param config: dictionary of the parameters
    :param units: list of units
    :param explain: list of explanations
    :param id: iterator for the id of the controls
    :param loc: location of the controls
    :return: list of controls
    """
    result = []

    for parameter, value in config.items():
        if parameter not in ConfigGetter.private_keys:
            parameter_name = parameter.replace("_", " ").lower().capitalize()
            if type(value) in {int, float}:
                if parameter.isnumeric():
                    result.append(dbc.Row([
                        dbc.Col([f"Period {int(parameter) + 1}:"], width="auto"),
                        dbc.Col(
                            dbc.InputGroup(
                                [
                                    dbc.Input(
                                        id={'type': 'config-input', 'index': id.__next__()},
                                        value=f"{value}",
                                        type="number"
                                    ),
                                    dbc.InputGroupText("kW" if "solar_panel_purchased" in loc else (
                                        "kWh" if "batteries_purchased" in loc else ""))
                                ]
                            )
                            , width=True)
                    ], className="my-2", align="center"))
                else:
                    result.append(dbc.Row([
                        dbc.Col([f"{parameter_name}:"], width="auto"),
                        dbc.Col([dbc.Button("?", id=f"{loc}-{parameter}",
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
    """
    Creates controls for the user to change the parameters of the senerio
    :param config: dictionary of the parameters
    :return: list of controls
    """
    with open(ConfigGetter.units_path) as f:
        units_data = json.load(f)
    units, explain = create_list(units_data, [], [])
    return get_parameters(config, units, explain)
