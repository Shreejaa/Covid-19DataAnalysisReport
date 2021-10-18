import dash_bootstrap_components as dbc

def NavigationBar():
    navigationBar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Vaccination Progress", href="/vaccination")),
            dbc.NavItem(dbc.NavLink("Spread Through out the world",href="/cases")),
        ],
        brand="Spread in USA",
        brand_href="/spread",
        sticky="top",
    )
    return navigationBar