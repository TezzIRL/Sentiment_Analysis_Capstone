# This is the main python file to be executed
# code example from @mcmanus_data_works: https://medium.com/@mcmanus_data_works/how-to-create-a-multipage-dash-app-261a8699ac3f


import webbrowser
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from navbar import create_navbar

from dash import (
    Dash,
    dcc,
    html,
    dash_table,
    Input,
    Output,
    State,
    register_page,
    callback,
)

import base64
import pandas as pd
import plotly.express as px
from ESA_Modules import Preprocessor
import datetime

webbrowser.get().open("http://127.0.0.1:8050")

email_preprocessor = Preprocessor()

# NAVBAR = create_navbar()

# Load your dataset
# df = pd.read_csv('4763.csv')  # Replace with your dataset file

# Get unique years from your dataset, including "All Years" option
# available_years = ['All Years'] + df['Year'].unique().tolist()

# custom font
FA621 = "https://use.fontawesome.com/releases/v6.2.1/css/all.css"
APP_TITLE = "Document Level Sentiment Analysis for Emails"

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.LUX,
        FA621,
    ],
    title=APP_TITLE,
)

# Define CSS styles to enhance the appearance
app.layout = dbc.Tabs(
    [
        dbc.Tab(
            label="Load and Preprocess",
            children=[
                html.Div(
                    [
                        html.H1(
                            "Load and Preprocess",
                            style={"color": "#0080FF", "font-size": "36px"},
                        ),
                        dcc.Upload(
                            id="upload-data",
                            children=html.Div(
                                ["Drag and Drop or ", html.A("Select Files")]
                            ),
                            style={
                                "width": "100%",
                                "height": "60px",
                                "lineHeight": "60px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                                "margin": "10px",
                            },
                            # Allow multiple files to be uploaded
                            multiple=True,
                        ),
                        html.Div(id="output-data-upload"),
                    ],
                    className="tab-content",
                    style={
                        "background-color": "#EFFBFB",
                        "padding": "20px",
                        "border-radius": "10px",
                    },
                ),
            ],
        ),
        dbc.Tab(
            label="Import Pre-Processed Emails",
            children=[
                html.Div(
                    [
                        html.H1(
                            "Import Pre-Processed Emails",
                            style={"color": "#0080FF", "font-size": "36px"},
                        ),
                        dcc.Upload(
                            id="upload-processed-data",
                            children=html.Div(
                                ["Drag and Drop or ", html.A("Select Files")]
                            ),
                            style={
                                "width": "100%",
                                "height": "60px",
                                "lineHeight": "60px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                                "margin": "10px",
                            },
                        ),
                        dcc.Download(id="download-processed-data"),
                        # Add more content for this scenario
                    ],
                    className="tab-content",
                    style={
                        "background-color": "#EFFBFB",
                        "padding": "20px",
                        "border-radius": "10px",
                    },
                ),
            ],
        ),
        dbc.Tab(
            label="Sentiment Classification",
            children=[
                html.Div(
                    [
                        html.H1(
                            "Sentiment Classification",
                            style={"color": "#0080FF", "font-size": "36px"},
                        ),
                        dcc.Upload(
                            id="upload-sentiment-data",
                            children=html.Div(
                                ["Drag and Drop or ", html.A("Select Files")]
                            ),
                            style={
                                "width": "100%",
                                "height": "60px",
                                "lineHeight": "60px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                                "margin": "10px",
                            },
                        ),
                        dcc.Download(id="download-sentiment-data"),
                        dcc.Textarea(
                            id="input-text",
                            placeholder="Enter text for sentiment analysis...",
                        ),
                        html.Div(
                            [
                                html.Button(
                                    "Analyze Sentiment",
                                    id="analyze-button",
                                    style={"margin-top": "10px"},
                                ),
                                html.Div(id="output-sentiment"),
                            ]
                        ),
                        # Add more content for this scenario
                    ],
                    className="tab-content",
                    style={
                        "background-color": "#EFFBFB",
                        "padding": "20px",
                        "border-radius": "10px",
                    },
                ),
            ],
        ),
        dbc.Tab(
            label="Export Emails",
            children=[
                html.Div(
                    [
                        html.H1(
                            "Export Emails",
                            style={"color": "#0080FF", "font-size": "36px"},
                        ),
                        html.Button(
                            "Export Processed Data",
                            id="export-processed-button",
                            n_clicks=0,
                        ),
                        # Add more content for this scenario
                    ],
                    className="tab-content",
                    style={
                        "background-color": "#EFFBFB",
                        "padding": "20px",
                        "border-radius": "10px",
                    },
                ),
            ],
        ),
        dbc.Tab(
            label="Visualization",
            children=[
                html.Div(
                    [
                        html.H1(
                            "Visualization",
                            style={"color": "#0080FF", "font-size": "36px"},
                        ),
                        dcc.Dropdown(
                            id="visualization-dropdown",
                            options=[
                                {"label": "Word Cloud", "value": "word-cloud"},
                                {"label": "Network Graph", "value": "network-graph"},
                                {"label": "Time Series", "value": "time-series"},
                                {"label": "Tree Map", "value": "tree-map"},
                                {"label": "Pie Chart", "value": "pie-chart"},
                            ],
                            value="word-cloud",
                        ),
                        # dbc.Row([
                        #     dbc.Col(dcc.Dropdown(
                        #         id='year-dropdown',
                        #         options=[{'label': year, 'value': year} for year in available_years],
                        #         value='All Years'  # Default to "All Years"
                        #     )),
                        # ]),
                        dcc.Graph(
                            id="visualization-graph",
                            style={
                                "width": "75%",
                                "height": "550px",
                            },  # Adjust the height as needed
                        ),
                    ],
                    style={
                        "background-color": "#EFFBFB",
                        "padding": "20px",
                        "border-radius": "10px",
                    },
                ),
            ],
        ),
    ]
)


@callback(
    Output("download-data", "data"),
    Input("upload-data", "filename"),
    Input("upload-data", "contents"),
)
def download_uploaded_data(filename, contents):
    if filename is not None:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        return {"content": decoded, "filename": filename}


@callback(
    Output("download-processed-data", "data"),
    Input("upload-processed-data", "filename"),
    Input("upload-processed-data", "contents"),
)
def download_uploaded_processed_data(filename, contents):
    if filename is not None:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        return {"content": decoded, "filename": filename}


@callback(
    Output("download-sentiment-data", "data"),
    Input("upload-sentiment-data", "filename"),
    Input("upload-sentiment-data", "contents"),
)
def download_uploaded_sentiment_data(filename, contents):
    if filename is not None:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        return {"content": decoded, "filename": filename}


@callback(
    Output("visualization-graph", "figure"),
    Input("visualization-dropdown", "value"),
    Input("year-dropdown", "value"),
)
def update_visualization(selected_option, selected_year):
    # if selected_year == 'All Years':
    #     filtered_df = df  # No filtering by year
    # else:
    #     filtered_df = df[df['Year'] == selected_year]

    if selected_option == "tree-map":
        # Create a Tree Map for the selected year
        # tree_map_fig = px.treemap(filtered_df, path=['Year', 'Label'], color='Label')
        # return tree_map_fig
        pass

    elif selected_option == "network-graph":
        # Create a Network Graph (Add your code here)
        return {}
    elif selected_option == "time-series":
        # Create a Time Series (Add your code here)
        return {}
    elif selected_option == "pie-chart":
        # Create a Pie Chart (Add your code here)
        return {}
    elif selected_option == "word-cloud":
        # Create a word cloud (Add your code here)
        return {}


@callback(
    Output("output-sentiment", "children"),
    Input("analyze-button", "n_clicks"),
    State("input-text", "value"),
)
def analyze_sentiment(n_clicks, input_text):
    # Perform sentiment analysis here and return the result
    return "Sentiment: Positive"  # Replace with your analysis result


# Parsing Content for Uploading Email Data - Not Good Code - CodeDebt - FIX!!!
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        # if 'csv' in filename:
        #     df = pd.read_csv(
        #         io.StringIO(decoded.decode('utf-8')))
        # elif 'xls' in filename:
        #     df = pd.read_excel(io.BytesIO(decoded))
        unprocessed_email = decoded.decode("utf-8")
        email_preprocessor.Simple_Clean(unprocessed_email)

    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    return html.Div(
        [
            html.H5(filename),
            html.H6(datetime.datetime.fromtimestamp(date)),
            dash_table.DataTable(
                data=email_preprocessor.get_dataframe().to_dict("records"),
                columns=[
                    {"name": i, "id": i}
                    for i in email_preprocessor.get_dataframe().columns
                ],
                style_data={
                    "whiteSpace": "normal",
                    "height": "auto",
                },
                fill_width=False,
            ),
            html.Hr(),
            html.Div("Raw Content"),
            html.Pre(
                contents[0:200] + "...",
                style={"whiteSpace": "pre-wrap", "wordBreak": "break-all"},
            ),
        ]
    )


@callback(
    Output("output-data-upload", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d)
            for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
        ]
        return children[-1]


server = app.server

if __name__ == "__main__":
    app.run_server(debug=False)