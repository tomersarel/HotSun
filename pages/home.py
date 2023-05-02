from imports import *

dash.register_page(__name__, path='/')
layout = html.Div([html.Img(src="assets/logo_no_bg_white.png", className="align-center",
                            style={"width": "80%"}),
                   html.H4("Shelly Kagan | Tomer Sarel | Daniel Hershkovitz",
                           style={"color": "white", "margin": "20px 0px 0px 0px"})],
                  style={"position": "absolute",
                                  "left": "50%",
                                  "top": "50%",
                                  "transform": "translate(-50%, -50%)",
                                  "-webkit-filter": "drop-shadow(5px 5px 5px #333333)",
                         "text-align": "center",
                                  "filter": "drop-shadow(5px 5px 5px #333333)"}, className="align-center")
