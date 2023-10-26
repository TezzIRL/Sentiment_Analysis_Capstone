# This is the main python file to be executed
# code example from @mcmanus_data_works: https://medium.com/@mcmanus_data_works/how-to-create-a-multipage-dash-app-261a8699ac3f


import webbrowser

import dash_bootstrap_components as dbc

import dash
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
from ESA_Modules import Sentiment_Classifier
import datetime
import io

webbrowser.get().open("http://127.0.0.1:8050")

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
            label="Home",
            children=[
                html.Div(
                    [
                        html.H1(
                            "Emails",
                            style={"color": "0080FF", "font-size": "36px"},
                        ),
                        html.Div(id="all-cleaned-emails"),
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
                        html.Div(
                            [
                                html.Button(
                                    "Download Cleaned Data",
                                    id="cleaned_data_download_btn_csv",
                                ),
                                dcc.Download(id="download-cleaned-data-csv"),
                            ]
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
                            id="upload-preprocessed-data",
                            children=html.Div(
                                ["Drag and Drop or ", html.A("Select File")]
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
                        html.Div(id="output-preprocessed-upload"),
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
                        html.Button(
                            "Display Non Classified",
                            id="list-non-classified-button",
                        ),
                        html.Button(
                            "Classify and Display",
                            id="list-classified-button",
                        ),
                        html.Div(id="output-sentiment"),
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
            label="Export Processed Emails",
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
                        ),
                        # Add more content for this scenario
                        dcc.Download(id="download-processed-data-csv"),
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
    ]
)


# Parsing Content for Uploading Email Data - Not Good Code - CodeDebt - FIX!!!
def load_preprocessed_csv(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            temp_df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))

            if cleaned_emails.empty:
                cleaned_emails = temp_df
            else:
                cleaned_emails.append(temp_df)
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    return html.Div(
        [
            dash_table.DataTable(
                # data=email_preprocessor.get_dataframe().to_dict("records"),
                data=cleaned_emails.to_dict("records"),
                columns=[{"name": i, "id": i} for i in cleaned_emails.columns],
                style_data={
                    "whiteSpace": "normal",
                    "height": "auto",
                },
                fill_width=False,
            ),
        ]
    )


@app.callback(
    Output(component_id="output-preprocessed-upload", component_property="children"),
    Input("upload-preprocessed-data", "contents"),
    State("upload-preprocessed-data", "filename"),
    State("upload-preprocessed-data", "last_modified"),
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            load_preprocessed_csv(list_of_contents, list_of_names, list_of_dates)
        ]
        return children


############################
# Upload Raw Emails - Clean - Append - Display
############################


# Parsing Content for Uploading Email Data - Not Good Code - CodeDebt - FIX!!!
def parse_contents(contents, filename, date, preprocessor):
    # split content into type and content
    content_type, content_string = contents.split(",")
    # decode content into readable string
    decoded = base64.b64decode(content_string)
    try:
        # decode to utf8
        unprocessed_email = decoded.decode("utf-8")
        # clean email
        preprocessor.Simple_Clean(unprocessed_email)
        # export cleaned emails dataframe
        cleaned_emails = preprocessor.get_dataframe()

    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    return dash_table.DataTable(
        # data=email_preprocessor.get_dataframe().to_dict("records"),
        data=cleaned_emails.to_dict("records"),
        columns=[{"name": i, "id": i} for i in cleaned_emails.columns],
        style_data={
            "whiteSpace": "normal",
            "height": "auto",
        },
        fill_width=False,
    )


# CALLBACK - Upload Raw Data
@app.callback(
    Output(component_id="output-data-upload", component_property="children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        email_preprocessor = Preprocessor()
        children = [
            parse_contents(c, n, d, email_preprocessor)
            for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
        ]
        return children[-1]


############################
# Download Cleaned Emails to CSV
############################


@app.callback(
    Output("download-cleaned-data-csv", "data"),
    Input("cleaned_data_download_btn_csv", "n_clicks"),
    State("output-data-upload", "children"),
    prevent_initial_call=True,
)
def cleaned_data_to_file(n_clicks, content):
    print(content)
    tempDF = pd.DataFrame(content["props"]["data"])
    return dcc.send_data_frame(tempDF.to_csv, "cleaned_emails.csv")


############################
# Upload Cleaned Email CSV - Append - Display
############################


############################
# Grab from Table -> Classify -> Display
############################


def populate_dash_table(dataframe):
    return dash_table.DataTable(
        # data=email_preprocessor.get_dataframe().to_dict("records"),
        data=dataframe.to_dict("records"),
        columns=[{"name": i, "id": i} for i in dataframe.columns],
        style_data={
            "whiteSpace": "normal",
            "height": "auto",
        },
        fill_width=False,
    )


@app.callback(
    Output(component_id="output-sentiment", component_property="children"),
    Input("list-classified-button", "n_clicks"),
    State("output-data-upload", "children"),
    prevent_initial_call=True,
)
def display_classified(mouse_clicks, data_table):
    tempDF = pd.DataFrame(data_table["props"]["data"])
    classifier = Sentiment_Classifier()
    classified_dataframe = classifier.Classify(tempDF)
    children = populate_dash_table(classified_dataframe)
    return children


############################
# Download Classified Emails to CSV
############################


@app.callback(
    Output("download-processed-data-csv", "data"),
    Input("export-processed-button", "n_clicks"),
    State("output-sentiment", "children"),
    prevent_initial_call=True,
)
def cleaned_data_to_file(n_clicks, content):
    print(content)
    tempDF = pd.DataFrame(content["props"]["data"])
    return dcc.send_data_frame(tempDF.to_csv, "sentiment_classified_emails.csv")


############################
# Visualise Processed Emails
############################

############################
# INIT -> RUNS THE PROGRAM #
############################
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)