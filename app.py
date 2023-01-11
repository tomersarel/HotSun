import json

import df_objects
from imports import *

logging.info("Start application")

application = Dash("Hot Sun", use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Start", href="/start")),
        dbc.NavItem(dbc.NavLink("Display Result", href="/show-energy-dist")),
        dbc.NavItem(dbc.NavLink("About Us", href="/show-energy-dist"))
    ],
    brand="Hot Sun",
    brand_href="/home",
    color="primary",
    dark=True,
    style={"height": "8vh"}
)

application.layout = html.Div([navbar,
                       dash.page_container,
                               dcc.Store(id="config", storage_type="memory", data=json.load(open("config.json")))
                       ], style={"overflow": "hidden"})
ConfigGetter.load_data()

if __name__ == '__main__':
    application.run_server(debug=True)
