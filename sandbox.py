from imports import *
import dash_html_components as html

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div(
    children=[
        html.H1("Hello, World!", className="align-center", style={"z-index": 1}),
        dcc.Graph(
            figure=go.Figure(
                data=[go.Pie(labels=['', ''], values=[70, 30],
                             marker=dict(
                                 colors=['#FFFFFF', '#00FF00']
                             ),
                             hoverinfo='none',
                             textinfo='none',
                             hole=.65,
                             showlegend=False,
                             sort=False
                             )],
                layout=go.Layout(annotations=[go.layout.Annotation(text="30%", showarrow=False,
                                                                   font=dict(size=35, color='black'))]),
                             ),
            config={
                "scrollZoom": False,
                "doubleClick": False,
                "displayModeBar": False,
                "showTips": False
            },
            style={"height": "350px", "width": "350px", "align-text": "center", "margin-top": "-100px", "z-index": -1}

        )
    ]
)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
