# Handles all logic for the visualisation page

from dash import html, register_page, callback

register_page(
    __name__,
    top_nav=True,
    path='/visualise'
)

def layout():
    layout = html.Div([
        html.H1(
            [
                "Data Visualise"
            ]
        )
    ])
    
    return layout
