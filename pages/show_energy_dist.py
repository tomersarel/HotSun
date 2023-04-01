import json

from imports import *
from df_objects import *
from pages.laod_display import generate_year_enr_graph, generate_day_enr_graph, dict_to_dataframe, get_parameter_wrapper

dash.register_page(__name__)

sidebar = html.Div([html.H4("Control Panel", className="text-center my-2"),
                    dbc.Button("Run", id="run", color="primary", style={"width": "45%"},
                               className="my-2 mx-2 text-center"),
                    dbc.Button("Cancel", id="cancel", color="primary", style={"width": "45%"},
                               className="my-2 mx-2 text-center"),
                    html.Div(id="paramerts", className="my-2 mx-2"),
                    dcc.Store(id="df_energy"), dcc.Store(id="df_finance"),
                    dcc.Location(id="location")],
                   style={"height": "90vh", "width": "100%",
                          "overflow-y": "auto", "overflow-x": "hidden",
                          "background": "rgba(255, 255, 255, 0.3)",
                          "backdrop-filter": "blur(8px)",
                          "border-radius": "10px"}, id="sidebar", className="mx-3")

layout = html.Div([html.Div(id="placeholder"), dbc.Row([dbc.Col(sidebar, width=3),
                                                        dbc.Col(
                                                            html.Div(style={"overflow": "auto", "height": "90vh",
                                                                            "background": "rgba(255, 255, 255, 0.3)",
                                                                            "backdrop-filter": "blur(8px)",
                                                                            "border-radius": "10px"}), id="display",
                                                            width=9)]),
                   ])


@callback(
    Output('yearlyEnergyGraph', 'figure'),
    Input('period_slider', 'value'),
    State("df_energy", "data")
)
def update_yearly_graph(value, df):
    fig = go.Figure(data=generate_year_enr_graph(value, value + 1, dict_to_dataframe(df), "D"),
                    layout=go.Layout(barmode='stack', title=f"{value} energy distribution"))
    fig.update_layout(bargap=0)
    return fig


@callback(
    Output('dailyGraph', 'figure'),
    Output('dailyGraph', 'style'),
    Input('yearlyEnergyGraph', 'clickData'),
    State("df_energy", "data"),
    prevent_initial_call=True
)
def update_daily_graph(clickData, df):
    date = datetime.datetime.strptime(clickData['points'][0]['x'], "%Y-%m-%d")
    return go.Figure(data=generate_day_enr_graph(date, dict_to_dataframe(df)),
                     layout=go.Layout(barmode='stack', title=f"{date.strftime('%d/%m/%Y')} energy distribution")), {
               "display": "block"}


def replace_json_value(config, parameter, val):
    """
    The function uses recursion to find where does the inital value is stored and replaces it with the users input
    """
    for key, inital_value in config.items():
        if isinstance(inital_value, dict):
            config[key] = replace_json_value(inital_value, parameter, val)
        elif key == parameter:
            config[key] = val
    return config


def replace_value(dict, hirarchy, value):
    if not hirarchy:
        return value

    dict[hirarchy[0]] = replace_value(dict[hirarchy[0]], hirarchy[1:], value)
    return dict


@callback(
    Output("config", "data", allow_duplicate=True),
    [Input({'type': 'config-input', 'index': ALL}, 'value'),
     Input({'type': 'config-parameter', 'index': ALL}, 'children')],
    State("config", "data"),
    prevent_initial_call=True
)
def change_config(val, parameter, config):
    trigger = ctx.triggered_id
    if trigger and type(val[trigger["index"]]) in [int, float]:
        config = replace_value(config, parameter[trigger["index"]].split("-")[1:], val[trigger["index"]])
    return config
