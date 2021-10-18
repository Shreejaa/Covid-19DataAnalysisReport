import dash
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
import math
from app import app

world = pd.read_csv("Data/worldometer_data.csv")
world['Continent']=world['Continent'].replace(to_replace = np.nan,value = "unknown")
world['WHO Region']=world['WHO Region'].replace(to_replace = np.nan,value = "unknown")
world['Population']=world['Population'].replace(to_replace = np.nan,value = 1)
world['NewCases']=world['NewCases'].replace(to_replace = np.nan,value = 0)
world['TotalDeaths']=world['TotalDeaths'].replace(to_replace = np.nan,value = 0)
world['NewDeaths']=world['NewDeaths'].replace(to_replace = np.nan,value = 0)
world['TotalRecovered']=world['TotalRecovered'].replace(to_replace = np.nan,value = 0)
world['NewRecovered']=world['NewRecovered'].replace(to_replace = np.nan,value = 0)
world['ActiveCases']=world['ActiveCases'].replace(to_replace = np.nan,value = 0)
world['Serious,Critical']=world['Serious,Critical'].replace(to_replace = np.nan,value = 0)
world['Tot Cases/1M pop']=world['Tot Cases/1M pop'].replace(to_replace = np.nan,value = 0)
world['Deaths/1M pop']=world['Deaths/1M pop'].replace(to_replace = np.nan,value = 0)
world['TotalTests']=world['TotalTests'].replace(to_replace = np.nan,value = 0)
world['Tests/1M pop']=world['Tests/1M pop'].replace(to_replace = np.nan,value = 0)

continents = world["Continent"].unique()
total = ["TotalTests", "TotalRecovered", "TotalDeaths"]

explain = "These graphs represents the cases, deaths, recoveries and tests from each continent"
explain += ", **Graph1** represents *the total cases and population based on each WHO region and countries of a continent*"
explain += ", **Graph2** represents *the most effected countries of each continent based on total cases*"
explain += ", **Graph3** represents *the serious and active cases of each WHO region for a continent* "
explain += ", **Graph4** represents *the total recovered, tested, deaths for different WHO regions for a continent*."

line_g = dbc.Col([
    dcc.Graph(id='line_effect')
],width=4)

cases = dbc.Row([
    dbc.Col([
        dcc.Graph(id="sunburst"),
    ],width=8),
    line_g
])

header = html.Div([
    html.Div(id='title',style={'fontSize': 32,'text-align':'center'}),
    dcc.Markdown(explain)
])

dropdown_c = dbc.Row([
    dbc.Col([
        html.Div([
            html.Label('Continents'),
            dcc.Dropdown(
                id = 'continent',
                options = [dict(label=x, value=x) for x in continents],
                value = 'Asia'
            )
        ])
    ],width=4)
])
dropdown_t = dbc.Row([
        dbc.Col([
            html.Div([
            html.Label('Types'),
            dcc.Dropdown(
                id = 'total_type',
                options = [dict(label=x, value=x) for x in total],
                value = total[1]
            )
        ])
        ],width=5)
])
categ_bar = dbc.Col([
    dcc.Graph(id="bar_plot")
],width=6)

box_g = dbc.Col([
    dropdown_t,
    dcc.Graph(id="box_plot")
],width=6)


layout = html.Div([
        html.Div([
        dbc.Card(
                dbc.CardBody([
                    header,
                    dropdown_c,
                    cases,
                    dbc.Row([
                        categ_bar,
                        box_g,
                    ]),
                ])
            )
        ])
    ])

@app.callback(
    Output("title", "children"), 
    [Input("continent", "value")])
def get_title(continent):
    return continent+" covid-19 spread statistics"

@app.callback(
    Output("line_effect", "figure"), 
    [Input("continent", "value")])
def most_effected(continent):
    world1 = world.loc[world["Continent"] == continent]
    world4 = world1.sort_values(by = 'TotalCases', ascending = False )
    if len(world4)>=10:
        world4 = world4.iloc[:10]
    line_g = go.Figure()
    line_g.add_trace(go.Scatter(x=world4["Tot Cases/1M pop"], y=world4['Country/Region'], name='Total Cases per million',
                            line=dict(color='blue', width=4)))
    line_g.add_trace(go.Scatter(x=world4["Deaths/1M pop"], y=world4['Country/Region'], name='Total Deaths per million',
                            line=dict(color='#800020', width=4)))
    line_g.add_trace(go.Scatter(x=world4["Tests/1M pop"], y=world4['Country/Region'], name='Total Tests per million',
                            line=dict(color='green', width=4)))
    line_g.update_layout(title="Most Affected Countries",plot_bgcolor='rgb(255,255,255)',height=700,width=400)
    return line_g


@app.callback(
    Output("sunburst", "figure"), 
    [Input("continent", "value")])
def sunburst_cases(continent):
    world1 = world.loc[world["Continent"] == continent]
    max_cases = world1['TotalCases'].max()/2
    sun_cases = px.sunburst(world1,path= ['WHO Region','Country/Region'],values='Population',
                    color='TotalCases', hover_data=['Country/Region','Population','TotalCases'],
                    color_continuous_scale=px.colors.sequential.Reds,
                    range_color = (0,max_cases),
                    color_continuous_midpoint=np.average(world1['TotalCases'], weights=world1['Population']))
    sun_cases.update_layout(autosize=False, width=700, height=700)
    return sun_cases
    

@app.callback(
    Output("box_plot", "figure"), 
    [Input("continent", "value"),
    Input("total_type","value")])    
def box_total(continent,types):
    world1 = world.loc[world["Continent"] == continent]
    box_type = go.Figure()
    box_type.add_trace(go.Box(y=world1['WHO Region'], x= world1[types] , name=types,
                    marker_color = 'rgb(128,0,0)'))
    box_type.update_layout(plot_bgcolor='rgb(255,255,255)', title=types)
    box_type.update_yaxes(title="WHO regions")
    box_type.update_xaxes(title=types)
    box_type.update_traces(orientation='h')
    return box_type
    

@app.callback(
    Output("bar_plot", "figure"), 
    [Input("continent", "value")])
def bar_cases(continent):
    world1 = world.loc[world["Continent"] == continent]
    world1['ActiveCases'] = world1['ActiveCases']/10
    world2 = pd.DataFrame(world1.groupby(['WHO Region']).agg({'ActiveCases':'sum','Serious,Critical':'sum'}).reset_index())
    cate_plot_cases = go.Figure()
    cate_plot_cases.add_trace(go.Bar(x=world2['WHO Region'], y=world2['ActiveCases'], name='Active Cases ',marker_color='rgb(255,192,155)'))
    cate_plot_cases.add_trace(go.Bar(x=world2['WHO Region'], y=world2['Serious,Critical'], name='Serious/Critical Cases',marker_color='rgb(128,0,0)'))
    max_c = math.floor(world2['ActiveCases'].max()+world2['Serious,Critical'].max())+10
    cate_plot_cases.update_layout(barmode='stack',plot_bgcolor='rgb(255,255,255)', title="Total Active and Serious Cases")
    cate_plot_cases.update_xaxes(categoryorder='category ascending',title="WHO regions")
    cate_plot_cases.update_yaxes(title='Active cases per 10 and Serious Cases')
    return cate_plot_cases


if __name__ == "__main__":
    app.run_server(debug=True)