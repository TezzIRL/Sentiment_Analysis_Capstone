# This is the main python file to be executed
# code example from @mcmanus_data_works: https://medium.com/@mcmanus_data_works/how-to-create-a-multipage-dash-app-261a8699ac3f


import webbrowser
from dash.dash import PreventUpdate

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
    ctx,
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
            label="Unclassified Emails",
            children=[
                html.Div(
                    [
                        html.H1(
                            "Unclassified Emails",
                            style={"color": "#0080FF", "font-size": "36px"},
                        ),
                        html.Div(id="table-unclassified-email"),
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
                            id="upload-raw-email",
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
                                    "Add Cleaned Emails to the Unclassified List",
                                    id="btn-add-to-unclassified-table",
                                    style={"margin-right": "10px"},
                                ),
                                html.Button(
                                    "Discard Emails",
                                    id="btn-clear-raw-output",
                                    style={"margin-right": "10px"},
                                ),
                                html.Button(
                                    "Download Cleaned Data",
                                    id="btn-download-cleaned",
                                ),
                                dcc.Download(id="download-cleaned-csv"),
                            ],
                            style={
                                "margin-bottom": "10px",
                                "margin-left": "10px",
                            },
                        ),
                        html.Div(id="output-cleaned-raw"),
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
                        html.Div(id="output-preprocessed-data"),
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
                            "Classify and Display",
                            id="btn-classify",
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


# # Parsing Content for Uploading Email Data - Not Good Code - CodeDebt - FIX!!!

# Converts a dataframe object into a data table
def populate_dash_table(dataframe):
    return dash_table.DataTable(
        data=dataframe.to_dict("records"),
        columns=[{"name": i, "id": i} for i in dataframe.columns],
        # Generic Styling
        style_data={
            "whiteSpace": "normal",
            "height": "auto",
        },
        fill_width=True,
    )

############################
# Upload Raw Emails - Clean - Append - Display
############################

# Parsing Content for Uploading Email Data - Not Good Code - CodeDebt - FIX!!!
def parse_raw_email_contents(contents, filename, date, preprocessor):
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

    new_dash_table = populate_dash_table(cleaned_emails)

    return new_dash_table


# CALLBACK - Upload Raw Data
@app.callback(
    Output(component_id="output-cleaned-raw", component_property="children"),
    Input("upload-raw-email", "contents"),
    State("upload-raw-email", "filename"),
    State("upload-raw-email", "last_modified"),
)
def update_raw_email_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        email_preprocessor = Preprocessor()
        children = [
            parse_raw_email_contents(c, n, d, email_preprocessor)
            for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
        ]
        # return only the last data table
        return children[-1]

############################
# Download Cleaned Emails to CSV
############################

# - WORKS
@app.callback(
    Output("download-cleaned-csv", "data"),
    Input("btn-download-cleaned", "n_clicks"),
    State("output-cleaned-raw", "children"),
    prevent_initial_call=True,
)
def cleaned_data_to_file(n_clicks, data_table):
    # if data_table is none, prevent return
    if (data_table is None):
        raise PreventUpdate
    else:
        # convert data table into a data frame so that it can be converted to a csv file
        tempDF = pd.DataFrame(data_table["props"]["data"])
        return dcc.send_data_frame(tempDF.to_csv, "cleaned_emails.csv")

############################
# Append Emails to Unclassified List - Remove Duplicates - Clear Upload Table
############################
@app.callback([
    Output('table-unclassified-email', 'children'),
    Output('output-cleaned-raw', 'children', allow_duplicate=True)
], [Input('btn-add-to-unclassified-table', 'n_clicks'),
    State("output-cleaned-raw", "children"),
    State("table-unclassified-email", "children")],
              prevent_initial_call=True)
def add_cleaned_emails_to_unclassified_table(clicks, raw_email_data_table, unclassified_table):
    # if there isnt any uploaded emails don't update
    if(raw_email_data_table is None):
        raise PreventUpdate
    else:
        tempRawDF = pd.DataFrame(raw_email_data_table["props"]["data"])
        # check if the unclassified table has been generated yet
        if (unclassified_table is not None):
            # convert table to dataframe
            tempUnclassifiedDF = pd.DataFrame(unclassified_table["props"]["data"])
            # concat the unclassified dataframe with the raw email dataframe
            unifiedDF = pd.concat([tempUnclassifiedDF, tempRawDF])
            # remove any duplicates that may have been included
            unifiedNoDupDF = unifiedDF.drop_duplicates()
            # convert dataframe back into a dash table
            unified_table = populate_dash_table(unifiedNoDupDF)
            # return unified table and none (removes the upload table)
            return unified_table, None
        else:
            new_table = populate_dash_table(tempRawDF)
            return new_table, None
        
############################
# Clear Upload Table
############################
@app.callback(
    Output('output-cleaned-raw', 'children', allow_duplicate=True),
    Input('btn-clear-raw-output', 'n_clicks'),
    State('output-cleaned-raw', 'children'),
    prevent_initial_call=True)
def clear_raw_email_output(clicks, data_table):
    if (data_table is None):
        raise PreventUpdate
    else:
        return None
    
############################
# Upload Cleaned Email CSV - Append - Display
############################
def load_preprocessed_csv(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    temp_df = ""
    try:
        if "csv" in filename:
            temp_df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])
    dash_table = populate_dash_table(temp_df)
    return dash_table


@app.callback(
    Output(component_id="output-preprocessed-data", component_property="children"),
    Input("upload-preprocessed-data", "contents"),
    State("upload-preprocessed-data", "filename"),
    State("upload-preprocessed-data", "last_modified"),
)
def load_preprocessed(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            load_preprocessed_csv(list_of_contents, list_of_names, list_of_dates)
        ]
        return children
    else:
        raise PreventUpdate

############################
# Grab from Table -> Classify -> Display
############################
@app.callback(
    Output(component_id="output-sentiment", component_property="children"),
    Input("btn-classify", "n_clicks"),
    State("table-unclassified-email", "children"),
    prevent_initial_call=True,
)
def display_classified(mouse_clicks, data_table):
    if data_table is None:
        raise PreventUpdate
    else:
        tempDF = pd.DataFrame(data_table["props"]["data"])
        classifier = Sentiment_Classifier()
        classified_dataframe = classifier.Classify(tempDF)
        children = populate_dash_table(classified_dataframe)
        return children


############################
# Download Classified Emails to CSV
############################
# @app.callback(
#     Output("download-processed-data-csv", "data"),
#     Input("export-processed-button", "n_clicks"),
#     State("output-sentiment", "children"),
#     prevent_initial_call=True,
# )
# def cleaned_data_to_file(n_clicks, content):
#     print(content)
#     tempDF = pd.DataFrame(content["props"]["data"])
#     return dcc.send_data_frame(tempDF.to_csv, "sentiment_classified_emails.csv")


############################
# Visualise Processed Emails
############################

############################
# INIT -> RUNS THE PROGRAM #
############################
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)