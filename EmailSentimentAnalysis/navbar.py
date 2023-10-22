from dash import html
import dash_bootstrap_components as dbc

def create_navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fa-brands fa-github"),
                        " "
                    ],
                    href="[YOUR GITHUB PPROFILE URL]",
                    target="_blank"
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fa-brands fa-medium"),
                        " "
                    ],
                    href="[YOUR MEDIUM PROFILE URL]",
                    target="_blank"
                )
            ),
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Menu",
                align_end=True,
                children=[
                    dbc.DropdownMenuItem("Home", href='/'),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Upload Data", href='/upload'),
                    dbc.DropdownMenuItem("Visualise", href='/visualise'),
                    dbc.DropdownMenuItem("Export", href='/export')
                ],
            ),
        ],
        
        brand='Home',
        brand_href="/",
        color="dark",
        dark=True
    )
    
    return navbar