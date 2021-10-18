import dash
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
from app import app


types = ['deaths','cases']
us_counties = pd.read_csv("Data/us-counties.csv",dtype={'fips':str})
us_counties['date']=pd.to_datetime(us_counties.date)
us_counties['date']= us_counties["date"].dt.strftime("%Y %m")
us_codes = pd.read_csv("Data/us_Codes.csv",dtype={'code':str})
del us_codes['Unnamed: 2']
usData = pd.merge(us_counties, us_codes, on='state', how='inner' )

explain = "These graphs represents the covid-19 statistics for different counties of USA."
explain += " **Graph1** represents *the USA map and the spread of covid based on cases and deaths.* "
explain += "**Graph2** represents *the spread in each county of a state, based on the data hovered on USA map.* "
explain += "**Graph3** represents *the spread in state through the timeline.* "

header = html.Div([
    html.Div([
         html.H2("USA Covid-19 Statistics"),
    ],style={'fontSize': 32,'text-align':'center'}),
    dcc.Markdown(explain)
])

radio_cases_deaths = dbc.Row([
                        dbc.Col([
                            html.P("Covid Deaths/cases  "),
                            dcc.RadioItems(
                                id='covid', 
                                options=[{'value': x, 'label': x} 
                                    for x in types],
                                value=types[0],
                                labelStyle={'display': 'inline-block'}
                                ),
                        ],width=3)
                    ])

map_radio = dbc.Col([
                    dcc.Graph(id="covid_map",
                        hoverData={
                            "points": [
                                {
                                    "curveNumber": 0,
                                    "pointNumber": 5,
                                    "pointIndex": 5,
                                    "location": "CO",
                                    "z": 821174,
                                    "customdata": [
                                        "Colorado"
                                    ]
                                }
                            ]
                        }
                    ),
                ],width=7)

line_g = dbc.Col([
                    dcc.Graph(id="time_series"),
                ],width=5)

time_g = dbc.Row([
                dbc.Col([
                    dcc.Graph(id="line_graph"),
                ],width=12) 
            ])

layout = html.Div([
        html.Div([
        dbc.Card(
                dbc.CardBody([
                    header,
                    radio_cases_deaths,
                    dbc.Row([
                        map_radio,
                        line_g
                    ]),
                    time_g
                ])
            )
        ])
    ])

@app.callback(
    Output("covid_map", "figure"), 
    [Input("covid", "value")])
def display_choropleth(types):
    us_covid = pd.DataFrame(usData.groupby(['state','code']).agg({'cases':'sum','deaths':'sum'}).reset_index())
    maxi = 0
    if types == 'deaths':
        maxi = us_covid["deaths"].max()
    else:
        maxi = us_covid["cases"].max()
    map_deaths = px.choropleth(us_covid, locations='code',
                       color = types,
                       color_continuous_scale=px.colors.sequential.Reds,
                       locationmode='USA-states',
                       hover_data={
                           'state': True,
                       },
                       range_color = (0,maxi),
                       title = "<b>Covid-19 "+types+" in USA</b>",
                       scope = 'usa')
    map_deaths.update_layout(title = '<b><i>Covid-19 '+types+' in USA</i></b>',width=700,height=500)
    return map_deaths


@app.callback(
    Output("line_graph", "figure"),
    Input("covid_map","hoverData"),
    Input("covid","value"))
def display_line_graph(hoverData,types):
    us_covid = pd.DataFrame(usData.groupby(['state','county']).agg({'cases':'sum','deaths':'sum'}).reset_index())
    us_covid = us_covid[ us_covid['state'] == hoverData['points'][0]['customdata'][0] ]
    fig = px.bar(us_covid, x="county", y=types, color=types,color_continuous_scale=px.colors.sequential.Reds)
    fig.update_layout(template="plotly_white"
    ,title="<b><i>Number of "+types+" in each county of "+hoverData['points'][0]['customdata'][0]+"</i></b>")
    return fig

@app.callback(
    Output("time_series","figure"),
    Input("covid_map","hoverData"),
    Input("covid","value"))
def display_time_series(hoverData,types):
    us_covid = pd.DataFrame(usData.groupby(['state','date']).agg({'cases':'sum','deaths':'sum'}).reset_index())
    x = us_covid['state'] == hoverData['points'][0]['customdata'][0]
    us_covid = us_covid[ us_covid['state'] == hoverData['points'][0]['customdata'][0] ].sort_values(by=["date"])
    fig = go.Figure(data=go.Scatter(x=us_covid["date"], y=us_covid[types],mode='lines+markers', line_color='#B90E0A'))
    fig.update_layout(template="plotly_white",
    title="<b><i>Number of "+types+" through out 2020 in "+hoverData['points'][0]['customdata'][0]+"</i></b>",width=500,height=500)
    return fig

