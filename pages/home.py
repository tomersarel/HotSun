from imports import *

dash.register_page(__name__, path='/')
layout = html.Div([html.Img(src="assets/logo_no_bg_white.png", className="align-center",
                            style={"position": "absolute",
                                   "height": "60vh",
                                   "width": "35vw",
                                   "left": "32vw",
                                   "top": "15vh",
                                   "-webkit-filter": "drop-shadow(5px 5px 5px #333333)",
                                   "filter": "drop-shadow(5px 5px 5px #333333)"}),
                   html.H4("Shelly Kagan | Tomer Sarel | Daniel Hershkovitz",
                           style={"position": "absolute", "left": "33%", "top": "82%",
                                  "-webkit-filter": "drop-shadow(5px 5px 5px #333333)",
                                  "filter": "drop-shadow(5px 5px 5px #333333)",
                                  "color": "white"
                                  })],
                  )
