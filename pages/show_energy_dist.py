from imports import *

dash.register_page(__name__)

sidebar = html.Div([html.H2("Parameters"), html.Button('Run', id="button")], style={"background-color": "primary", "height": "100%"})

display_summery = html.Div()
display_energy = html.Div([dcc.Slider(id="period_slider",
                                      min=2017,
                                      max=2017 + 32,
                                      step=1,
                                      marks={i: '{}'.format(i) for i in
                                             range(2017, 2017 + 32, 1)},
                                      value=2017),
                           dcc.Graph(id='yearlyGraph'),
                           dcc.Graph(id='dailyGraph')
                           ])
display_finance = html.Div()

display = dbc.Accordion([dbc.AccordionItem(display_summery, title='Summery'),
                         dbc.AccordionItem(display_energy, title='Energy'),
                         dbc.AccordionItem(display_finance, title='Finance')])

layout = dbc.Row([dbc.Col(sidebar, width=2),
                  dbc.Col(display, width=10)], style={"height": "100%"})


def generate_year_enr_graph(year):
    data = pd.read_csv(f"simulation output//period{year - 2017}.csv", parse_dates=['Date'], dayfirst=True,
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
    Input('yearlyGraph', 'clickData'),
    prevent_initial_call=True
)
def update_daily_graph(clickData):
    date = datetime.datetime.strptime(clickData['points'][0]['x'], "%Y-%m-%d")
    return go.Figure(data=generate_day_enr_graph(date),
                     layout=go.Layout(barmode='stack', title=f"{date.strftime('%d/%m/%Y')} energy distribution"))
