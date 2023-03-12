from imports import *

dash.register_page(__name__)
layout = html.Div([html.Img(src="assets/logo_no_bg.png", className="align-center", height="300"),
                   html.H4("Shelly Kagan | Tomer Sarel | Daniel Hershkovitz")],
                  className="align-center", style={"position": "absolute", "left": "50%", "top": "10%"})
