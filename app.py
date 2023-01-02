from imports import *
import hourly_strategy

logging.info("Start application")
app = Dash("Hot Sun", use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Start", href="/run-simulation")),
        dbc.NavItem(dbc.NavLink("Display Result", href="/show-energy-dist")),
        dbc.NavItem(dbc.NavLink("About Us", href="/show-energy-dist"))
    ],
    brand="Hot Sun",
    brand_href="/home",
    color="primary",
    dark=True,
    style={"height": "8vh"}
)

app.layout = html.Div([navbar,
                       dash.page_container
                       ], style={"overflow": "hidden"})
ConfigGetter.load_data()

if __name__ == '__main__':
    app.run_server(debug=True)
