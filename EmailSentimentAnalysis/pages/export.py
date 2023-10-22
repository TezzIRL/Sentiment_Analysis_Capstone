# Handles all logic for the export webpage

from dash import html, register_page, callback

register_page(
    __name__,
    top_nav=True,
    path='/export'
)

def layout():
    layout = html.Div([
        html.H1(
            [
                "Export Data"
            ]
        )
    ])
    
    return layout
