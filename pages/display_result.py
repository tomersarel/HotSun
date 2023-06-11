import json

from imports import *
from df_objects import *
from pages.laod_display import get_figure, generate_daily_energy_graph_by_date, dict_to_dataframe, generate_energy_graph_by_year_range

dash.register_page(__name__)

sidebar = html.Div([html.H4("Control Panel", className="text-center my-2"),
                    dbc.Button("Run", id="run", color="primary", style={"width": "45.5%", "margin": "2.5% 1.5% 2.5% 3%"},
                               className="text-center"),
                    dbc.Button("Cancel", id="cancel", color="primary", style={"width": "45.5%", "margin": "2.5% 3% 2.5% 1.5%"},
                               className="text-center"),
                    html.Div(id="paramerts", className="my-2 mx-2"),
                    dcc.Store(id="df_energy"), dcc.Store(id="df_finance"),
                    dcc.Location(id="location")],
                   style={"height": "90vh", "width": "100%",
                          "overflow-y": "auto", "overflow-x": "hidden",
                          "background": "rgba(255, 255, 255, 0.3)",
                          "backdrop-filter": "blur(8px)",
                          "border-radius": "10px"}, id="sidebar", className="mx-3")

layout = html.Div(dbc.Row([dbc.Col(sidebar, width=3),
                           dbc.Col(
                               html.Div(style={"overflow": "auto", "height": "90vh",
                                               "background": "rgba(255, 255, 255, 0.3)",
                                               "backdrop-filter": "blur(8px)",
                                               "border-radius": "10px"}), id="display",
                               width=9)]))


@callback(
    Output('yearlyEnergyGraph', 'figure'),
    Input('period_slider', 'value'),
    State("df_energy", "data")
)
def update_yearly_graph(value, df):
    """
    The function updates the yearly energy graph
    :param value: the year to display
    :param df: the energy dataframe
    :return: the updated graph
    """
    return get_figure(generate_energy_graph_by_year_range(value, value + 1, dict_to_dataframe(df), "D"),
                      f"{value} energy distribution",
                      "Date", "Energy [kWh]", bargap=0)


@callback(
    Output('dailyGraph', 'figure'),
    Output('dailyGraph', 'style'),
    Input('yearlyEnergyGraph', 'clickData'),
    State("df_energy", "data"),
    prevent_initial_call=True
)
def update_daily_graph(click_data, df):
    """
    The function updates the daily energy graph
    :param click_data: the date to display
    :param df: the energy dataframe
    :return: the updated graph
    """
    date = datetime.datetime.strptime(click_data['points'][0]['x'], "%Y-%m-%d")
    return get_figure(generate_daily_energy_graph_by_date(date, dict_to_dataframe(df)),
                      f"{date.strftime('%d/%m/%Y')} energy distribution",
                        "Hour", "Energy [kWh]"), {"display": "block"}


def replace_value(dict, hierarchy, value):
    """
    The function replaces the value of a parameter in a dictionary
    :param dict: the dictionary
    :param hierarchy: the hierarchy parameter to replace
    :param value: the new value
    :return: the updated dictionary
    """
    if not hierarchy:
        return value

    dict[hierarchy[0]] = replace_value(dict[hierarchy[0]], hierarchy[1:], value)
    return dict


@callback(
    Output("config", "data", allow_duplicate=True),
    Input({'type': 'config-input', 'index': ALL}, 'value'),
    State("config", "data"),
    prevent_initial_call=True
)
def change_config(val, config):
    """
    The function changes the config file
    :param val: the new value
    :param config: the config file
    """
    trigger = ctx.triggered_id
    if trigger and type(val[trigger["index"]]) in [int, float]:
        config = replace_value(config, ConfigGetter.get_locations(config)[trigger["index"]].split("-")[1:], val[trigger["index"]])

    return config
