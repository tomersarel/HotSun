import pandas as pd

from imports import *
import dash_html_components as html

"""# Initialize the Dash app
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
)"""

"""df = pd.read_csv("data/highschool_consumption.csv")
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
df.set_index("Date", inplace=True)
curr_year = df.index[0].year
dfs = [df]
while curr_year < 2050:
    df.index = df.index + pd.DateOffset(years=1)
    df = df * 1.05
    dfs.append(df)
    curr_year += 1
df = pd.concat(dfs)
df.index = df.index - pd.DateOffset(years=1)
df.reindex()
df.fillna(method='ffill')
print(df)"""


df = pd.read_csv("data/highschool_consumption.csv")
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
df.set_index("Date", inplace=True)
start_year = df.index[0].year
curr_year = start_year
dfs = []
while curr_year < 2050:
    dfs.append(df)
    df = df.multiply(1.05)
    curr_year += 1

df = pd.concat(dfs, ignore_index=True)
last_row = pd.DataFrame(df.iloc[-1]).transpose()
missing_days = (datetime.datetime(year=2050, month=1, day=1) - datetime.datetime(year=start_year, month=1, day=1)).days - len(df.index)
if missing_days > 0:
    additional_rows = pd.concat([last_row] * missing_days)
    print(additional_rows)
    df = pd.concat([df, additional_rows], ignore_index=True)
df['Date'] = pd.date_range(start=datetime.datetime(year=start_year, month=1, day=1), periods=len(df.index), freq='D')
print(df)
