from imports import *
from df_objects import *
from pages.laod_display import generate_year_enr_graph, generate_day_enr_graph, dict_to_dataframe

dash.register_page(__name__)

sidebar = html.Div([html.H4("Control Panel", className="text-center"),
                    dbc.Button("Run", id="run", color="primary", style={"width": "45%"}, className="my-2 mx-2 text-center"),
                    dbc.Button("Cancel", id="cancel", color="primary", style={"width": "45%"},
                               className="my-2 mx-2 text-center"),
                    html.Div(id="paramerts", className="my-2 mx-2"),
                    dcc.Store(id="df_energy"), dcc.Store(id="df_finance"),
                   dcc.Location(id="location")],
                   style={"height": "92vh", "width": "100%",
                          "overflow-y": "auto", "overflow-x": "hidden"}, id="sidebar", className="my-3")

layout = html.Div([html.Div(id="placeholder"), dbc.Row([dbc.Col(sidebar, width=3),
                                                        dbc.Col(id="display", width=9)]),
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

'''
The function uses recursion to find where does the inital value is stored and replaces it with the users input
'''
def replace_json_value(confi, parameter, val):
     for key, inital_value in confi.items():
            if isinstance(inital_value, dict):
                replace_json_value(inital_value, parameter, val)
            elif key == key:
                confi[key] = val


@callback(
    Output("config", "data", allow_duplicate=True),
    [Input({'type': 'config-input', 'index': ALL}, 'value'),
    Input({'type': 'config-parameter', 'index': ALL}, 'value')],
    State("config", "data"),
    prevent_initial_call='initial_duplicate'
)
def change_config(val,parameter,confi):
    trigger = ctx.triggered_id
    if trigger:
       replace_json_value(confi, parameter, val)

    with open(ConfigGetter.json_path, 'w') as f:
        json.dump(confi, f, indent = 4)

    return confi