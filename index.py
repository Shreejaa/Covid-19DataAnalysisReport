import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import app
from apps import spread, navigation, wcases, vaccination

navbar = navigation.NavigationBar()

app.layout = html.Div([
    dcc.Location(id = 'url', refresh = False),
    navbar,
    html.Div(id = 'page-content')
])

@app.callback(Output('page-content', 'children'),
            [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/cases':
        return wcases.layout
    elif pathname == '/vaccination':
        return vaccination.layout
    else:
        return spread.layout


if __name__ == '__main__':
    app.run_server(debug=True)