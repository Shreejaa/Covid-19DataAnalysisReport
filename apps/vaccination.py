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


vaccines = pd.read_csv('Data/country_vaccinations.csv')
vaccines['iso_code'] = vaccines['iso_code'].replace(to_replace = np.nan,value = "unknown")
vaccines['total_vaccinations'] = vaccines['total_vaccinations'].replace(to_replace = np.nan,value = 0)
vaccines['people_vaccinated'] = vaccines['people_vaccinated'].replace(to_replace = np.nan,value = 0)
vaccines['people_fully_vaccinated'] = vaccines['people_fully_vaccinated'].replace(to_replace = np.nan,value = 0)
vaccines['daily_vaccinations_raw'] = vaccines['daily_vaccinations_raw'].replace(to_replace = np.nan,value = 0)
vaccines['total_vaccinations_per_hundred'] = vaccines['total_vaccinations_per_hundred'].replace(to_replace = np.nan,value = 0)
vaccines['people_vaccinated_per_hundred'] = vaccines['people_vaccinated_per_hundred'].replace(to_replace = np.nan,value = 0)
vaccines['people_fully_vaccinated_per_hundred'] = vaccines['people_fully_vaccinated_per_hundred'].replace(to_replace = np.nan,value = 0)
vaccines['daily_vaccinations_per_million'] = vaccines['daily_vaccinations_per_million'].replace(to_replace = np.nan,value = 0)
vaccines['daily_vaccinations'] = vaccines['daily_vaccinations'].replace(to_replace = np.nan,value = 0)
vaccines['date']=pd.to_datetime(vaccines.date)
vaccines['date']= vaccines["date"].dt.strftime("%Y %m")
max_date = vaccines['date'].max()
min_date = vaccines['date'].min()



vaccines_source = vaccines.loc[vaccines['people_fully_vaccinated'] != 0]
v101 = vaccines['total_vaccinations'] != 0
v102 = vaccines['people_fully_vaccinated'] != 0

vaccines_namewise = vaccines.loc[v101 & v102]

source = vaccines_source['source_name'].unique()
vaccineName = vaccines_namewise['vaccines'].unique()




explain = "These graphs represents the covid-19 vaccination progress for different countries in the world."
explain += " **Graph1** represents *the world map describing the fully vaccinated people through the world based on timelines*. "
explain += "**Graph2** represents *the fully vaccinated people by the number of vaccinations present in each country and the type of vaccines*. "
explain += "**Graph3** represents *the total vaccines present per 100 and daily vaccinated people through the world based on different sources*. "


def create_bubble_map():
    vacc_tc_fvp3=vaccines.groupby(by=['country','iso_code','date'],sort=False).sum().groupby(level=[0]).cumsum().reset_index()
    vacc_tc_fvp3 = vacc_tc_fvp3.sort_values(by='date',ascending=True)
    fig2 = px.scatter_geo(vacc_tc_fvp3, locations="iso_code", 
                         hover_name="country", size="people_fully_vaccinated", animation_frame="date",
                         projection="natural earth")
    fig2.update_layout(height=700,width=1200,title="<b>Fully vaccinated population</b>",plot_bgcolor='rgb(255,255,255)')
    return fig2

vaccines_dd = dbc.Col([
        html.Div([
            html.Label('Combinations of Vaccines'),
            dcc.Dropdown(
                id = 'vaccine',
                options = [dict(label=x, value=x) for x in vaccineName],
                value = vaccineName[0]
            )
        ])
    ],width=6)

source_dd = dbc.Col([
            html.Div([
                html.Label('Source Name'),
                dcc.Dropdown(
                    id = 'sourceName',
                    options = [dict(label=x, value=x) for x in source],
                    value = source[0]
                )
            ])
    ],width=6)

scatter_plot =dbc.Col([
        dcc.Graph(id='scatter')
        ],width=6)


scatter_geo = dbc.Row([
    dcc.Graph(id='geo',figure = create_bubble_map())
])

bubble =dbc.Col([
        dcc.Graph(id='bubble')
    ],width=6) 

header = html.Div([
    html.Div([
         html.H2("Covid-19 Vaccination progress through the World"),
    ],style={'fontSize': 32,'text-align':'center'}),
    dcc.Markdown(explain)
])

layout = html.Div([
        html.Div([
        dbc.Card(
                dbc.CardBody([
                    header,
                    scatter_geo,
                    dbc.Row([
                        vaccines_dd,
                        source_dd,
                    ]),
                    dbc.Row([
                        scatter_plot,
                        bubble,
                    ])
                ])
            )
        ])
    ])

@app.callback(
    Output("scatter", "figure"), 
    [Input("vaccine", "value")])
def create_scatter_plot(vaccine):
    v1 = vaccines_namewise['vaccines'] == vaccine
    vaccines1 = vaccines_namewise[v1]
    fig1 = px.scatter(vaccines1, x="total_vaccinations", y="people_fully_vaccinated",hover_name="country")
    fig1.update_layout(height=500,width=600,title="<b>Total vaccinations and fully vaccinated people<br> for vaccine "+vaccine+"</b>",plot_bgcolor='rgb(255,255,255)')
    return fig1


@app.callback(
    Output("bubble", "figure"), 
    [Input("sourceName", "value")])
def create_bubble_plot(sourcen):
    vaccines4 =  vaccines[vaccines['source_name']==sourcen]
    fig3 = px.scatter(vaccines4, x="total_vaccinations_per_hundred", y="daily_vaccinations_per_million",
	         size= 'people_fully_vaccinated_per_hundred',hover_name="country")
    fig3.update_layout(height=500,width=600,title="<b>Total vaccinations and daily vaccination<br> by "+sourcen+"</b>",plot_bgcolor='rgb(255,255,255)')
    return fig3

