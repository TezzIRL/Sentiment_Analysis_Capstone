# This is the main python file to be executed
# code example from @mcmanus_data_works: https://medium.com/@mcmanus_data_works/how-to-create-a-multipage-dash-app-261a8699ac3f


import webbrowser
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from navbar import create_navbar


webbrowser.get().open("http://127.0.0.1:8050")


