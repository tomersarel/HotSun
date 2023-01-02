from imports import *

dash.register_page(__name__)

sidebar = html.Div([html.H3("Control Panel"),
                    html.Div(dbc.Button("Run", href="/run-simulation", color="primary", style={"width": "80%"}))],
                   style={"height": "92vh"}, className="text-center")
display_summery = html.Div([
    dbc.Card([dbc.CardBody([
        html.H1(f"{i * 75 % 129}$", className="card-title", style={"text-align": "center", "font-size": 48}),
        html.H4(f"Parameter {i}", className="card-title", style={"text-align": "center"}),
        html.P(
            "description of the paramter",
            className="card-text",
        )])], style={"width": "18rem"}, className="mx-2 my-2") for i in range(8)
], className="row")
display_energy = html.Div([dcc.Slider(id="period_slider",
                                      min=ConfigGetter["START_YEAR"],
                                      max=ConfigGetter["END_YEAR"],
                                      step=1,
                                      marks={i: '{}'.format(i) for i in
                                             range(ConfigGetter["START_YEAR"], ConfigGetter["END_YEAR"])},
                                      value=ConfigGetter["START_YEAR"]),
                           dcc.Graph(id='yearlyGraph', style={"height": "600px"}),
                           dcc.Graph(id='dailyGraph', style={"display": "None"})
                           ])
display_finance = html.Div()

display = html.Div(dbc.Accordion([dbc.AccordionItem(display_summery, title='Summery'),
                                  dbc.AccordionItem(display_energy, title='Energy'),
                                  dbc.AccordionItem(display_finance, title='Finance')],
                                 always_open=True), style={"overflow": "auto", "height": "92vh"})

layout = dbc.Row([dbc.Col(sidebar, width=2),
                  dbc.Col(display, width=10)])


def generate_year_enr_graph(year):
    data = pd.read_csv(f"simulation output//period{year - ConfigGetter['START_YEAR']}.csv", parse_dates=['Date'], dayfirst=True,
                       index_col=['Date'])
    data = data.resample('D').sum()
    return [go.Bar(x=data.index, y=data[col], name=col) for col in data.columns]


@callback(
    Output('yearlyGraph', 'figure'),
    Input('period_slider', 'value'))
def update_yearly_graph(value):
    return go.Figure(data=generate_year_enr_graph(value),
                     layout=go.Layout(barmode='stack', title=f"{value} energy distribution"))


def generate_day_enr_graph(date):
    df = pd.read_csv(f"simulation output//period{date.year - 2017}.csv", parse_dates=['Date'], dayfirst=True,
                     index_col=['Date'])
    df = df[(df.index >= date) & (df.index < date + datetime.timedelta(days=1))]
    return [go.Bar(x=df.index.hour, y=df[col], name=col) for col in df.columns]


@callback(
    Output('dailyGraph', 'figure'),
    Output('dailyGraph', 'style'),
    Input('yearlyGraph', 'clickData'),
    prevent_initial_call=True
)
def update_daily_graph(clickData):
    date = datetime.datetime.strptime(clickData['points'][0]['x'], "%Y-%m-%d")
    return go.Figure(data=generate_day_enr_graph(date),
                     layout=go.Layout(barmode='stack', title=f"{date.strftime('%d/%m/%Y')} energy distribution")), {"display": "block"}
