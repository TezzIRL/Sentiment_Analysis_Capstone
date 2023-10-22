# This is the main python file to be executed
# code example from @mcmanus_data_works: https://medium.com/@mcmanus_data_works/how-to-create-a-multipage-dash-app-261a8699ac3f


import webbrowser
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from navbar import create_navbar


webbrowser.get().open("http://127.0.0.1:8050")

NAVBAR = create_navbar()

#custom font
FA621 = "https://use.fontawesome.com/releases/v6.2.1/css/all.css"
APP_TITLE = "First Dash App"

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.LUX,
        FA621,
    ],
    title=APP_TITLE,
    use_pages=True,
)

app.layout = dcc.Loading(
    id='loading_page_content',
    children=[
        html.Div(
            [
                NAVBAR,
                dash.page_container
            ]
        )
    ],
    color='primary',
    fullscreen=True
)

server = app.server

if __name__ == '__main__':
    app.run_server(debug=False)