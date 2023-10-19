# This file will contain all Interace logic
from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

class Interface:
    def __init__(self, window_title):
        self.window_title = window_title
        self.running = False
        
        self.app = Dash(window_title)
        self.app.layout = html.Div(children=[html.H1(children='Hello Dash')])
        
    def run(self):
        self.running = True
        self.app.run()
        

        
