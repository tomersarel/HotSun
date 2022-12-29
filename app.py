from imports import *
import hourly_strategy

logging.info("Start application")
app = Dash("Hot Sun", use_pages=True)

app.layout = html.Div([html.H1("Hot Sun"),
                       html.Div([html.Div(dcc.Link("run", href="/run-simulation"))]),
                       dash.page_container
                       ])
ConfigGetter.load_data()

if __name__ == '__main__':
    app.run_server(debug=True)
