from imports import *

dash.register_page(__name__, path='/')
layout = html.Div([html.Img(src="assets/logo_no_bg.png", className="align-center", style={"position": "absolute", "width": "40%", "left": "30%", "top": "10%"}),
                   html.H4("Shelly Kagan | Tomer Sarel | Daniel Hershkovitz", style={"position": "absolute", "left": "33%", "top": "82%"})],
                  )
