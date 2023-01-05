import json

from imports import *

dash.register_page(__name__)


def get_screen(i, period, start, end, lon, lat):
    if i == 0:
        town_select = dcc.Dropdown(id="select",
                                   placeholder='Select your city',
                                   options=[{"label": city, "value": f"{loc[0]}/{loc[1]}"} for (city, loc) in
                                            df_objects.get_town_loc_by_name()], persistence=True,
                                   persistence_type='local', value="Tel Aviv-Yafo")
        return html.Div([dbc.Row([dbc.Col(html.H2("Choose a city"))]),
                         dbc.Row([dbc.Col(html.Big("description of this paramter like thie like"))]),
                         dbc.Row([dbc.Col(html.H1(" "))]),
                         dbc.Row([dbc.Col(town_select)])],
                        style={"padding": "20px"})
    if i == 1:
        return html.Div([dbc.Row([dbc.Col(html.H2("Choose date range"))]),
                         dbc.Row([dbc.Col(html.Big("description of this paramter like thie like"))]),
                         dbc.Row([dbc.Col(html.H1(" "))]),
                         dbc.Row([dbc.Col(dcc.DatePickerRange(id="range-pick",
                                                              min_date_allowed=datetime.date(2017, 1, 1),
                                                              start_date=start,
                                                              end_date=end,
                                                              max_date_allowed=datetime.date(2050, 1, 1)))])
                         ],
                        style={"padding": "20px"})
    if i == 2:
        return html.Div([dbc.Row([dbc.Col(html.H2("Choose period length"))]),
                         dbc.Row([dbc.Col(html.Big("description of this paramter like thie like"))]),
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
                         ))])],
                        style={"padding": "20px"})
    if i == 3:
        return html.Div([dbc.Row([dbc.Col(html.H2("Enter purchase strategy"))]),
                         dbc.Row([dbc.Col(html.Big("description of this paramter like thie like"))]),
                         dbc.Row([dbc.Col(html.H1(" "))]),
                         dbc.Row([dbc.Col(dcc.Upload(
                             id='upload-data',
                             children=html.Div([
                                 'Drag and Drop or ',
                                 html.B('Select Files')
                             ]),
                             style={
                                 'width': '100%',
                                 'height': '60px',
                                 'lineHeight': '60px',
                                 'borderWidth': '1px',
                                 'borderStyle': 'dashed',
                                 'borderRadius': '5px',
                                 'textAlign': 'center',
                                 'margin': '10px'
                             },
                             # Allow multiple files to be uploaded
                             multiple=False
                         ))])
                         ],
                        style={"padding": "20px"})
    if i == 4:
        return html.Div([dbc.Row([dbc.Col(html.H2("Run the simulation"))]),
                         dbc.Row([dbc.Col(html.Big(f"{start}-{end} for period of {period} days at {lat}/{lon}"))]),
                         dbc.Row([dbc.Col(html.P("\n\n\n"))]),
                         dbc.Row([dbc.Col(dbc.Button("Run", href="/show-energy-dist"))])
                         ],
                        style={"padding": "20px"})


center = {"position": "absolute", "top": "50%", "-ms-transform": "translateY(-50%)", "transform": "translateY(-50%)"}
bottom = {"position": "absolute", "top": "95%", "-ms-transform": "translateY(-50%)", "transform": "translateY(-50%)"}

layout = html.Div([dbc.Card(
    [dbc.CardBody([html.Div([dbc.Row([dbc.Col(dbc.Button("Previous", id="prev", n_clicks=0, style=center), width=2),
                                      dbc.Col(id="content", width=8),
                                      dbc.Col(dbc.Button("Next", id="next", n_clicks=0, style=center), width=2)]),
                             dbc.Row(dbc.Col(html.Small("1/5", style=bottom, id="step_num"), width=2),
                                     justify="center")])])]
    , style={"display": "block", "width": "60%", "height": "300px", "padding": "10px", "margin": "10% 20% 10% 20%"})
    , dcc.Store(id="city-lon-lat", storage_type='local')
    , dcc.Store(id="date-start", storage_type='local', data=datetime.datetime.strptime(ConfigGetter['START_DATE'], ConfigGetter['TIME_FORMAT']))
    , dcc.Store(id="date-end", storage_type='local', data=datetime.datetime.strptime(ConfigGetter['END_DATE'], ConfigGetter['TIME_FORMAT']))
    , dcc.Store(id="period-length", storage_type='local', data=ConfigGetter['PERIODS_DAYS_AMOUNT'])
    , dcc.Store(id="purchase-strategy", storage_type='local', data={})])


@callback(
    Output('content', 'children'),
    Output('prev', 'disabled'),
    Output('next', 'disabled'),
    Output('step_num', 'children'),
    Input('next', 'n_clicks'),
    Input('prev', 'n_clicks'),
    State("period-length", "data"),
    State("date-start", "data"), State("date-end", "data"),
    State('city-lon-lat', 'data')
)
def update_output(n_clicks1, n_clicks2, period, start, end, loc):
    return get_screen(n_clicks1 - n_clicks2, period, start, end, loc[0], loc[1]), n_clicks1 - n_clicks2 == 0, n_clicks1 - n_clicks2 == 4, f"{n_clicks1 - n_clicks2 + 1}/5"


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
    if length is None:
        return 365, prev
    DAYS = {"years": 365, "months": 30, "days": 1}
    ctx = dash.callback_context
    if not ctx.triggered:
        chosen = prev
    else:
        chosen = ctx.triggered[0]["prop_id"].split(".")[0]
    print(length, chosen, length * DAYS[chosen])
    return length * DAYS[chosen], chosen


@callback(Output("date-start", "data"), Output("date-end", "data"),
          Input('range-pick', 'start_date'),
          Input('range-pick', 'end_date')
          )
def foo(start, end):
    print(start, end)
    """start = datetime.datetime.strptime(start, '%Y-%m-%d').strftime(ConfigGetter['TIME_FORMAT'])
    end = datetime.datetime.strptime(end, '%Y-%m-%d').strftime(ConfigGetter['TIME_FORMAT'])"""
    return start, end


@callback(
    Output('city-lon-lat', 'data'),
    Input('select', 'value')
)
def update_output(value):
    return float(value.split("/")[0]), float(value.split("/")[1])
