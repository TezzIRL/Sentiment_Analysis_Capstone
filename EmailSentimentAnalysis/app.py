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

import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from scipy.interpolate import make_interp_spline
import numpy as np
import networkx as nx
import plotly.graph_objs as go

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
            label="Load Raw Emails",
            children=[
                html.Div(
                    [
                        html.H1(
                            "Load Raw Emails",
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
                                    "Add to the Unclassified List",
                                    id="btn-add-to-unclassified-table",
                                    style={"margin-right": "10px"},
                                ),
                                html.Button(
                                    "Discard",
                                    id="btn-clear-raw-output",
                                    style={"margin-right": "10px"},
                                ),
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
                        html.Div(
                            [
                                html.Button(
                                    "Add to the Unclassified List",
                                    id="btn-csv-to-unclassified",
                                    style={"margin-right": "10px"},
                                ),
                                html.Button(
                                    "Discard",
                                    id="btn-clear-csv",
                                    style={"margin-right": "10px"},
                                ),
                            ],
                            style={
                                "margin-bottom": "10px",
                                "margin-left": "10px",
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
            label="Export",
            children=[
                html.Div(
                    [
                        html.H1(
                            "Export Emails",
                            style={"color": "#0080FF", "font-size": "36px"},
                        ),
                        html.Button(
                            "Export Cleaned Email Data",
                            id="btn-download-cleaned",
                            style={"margin-right": "10px"},
                        ),
                        dcc.Download(id="download-cleaned-csv"),
                        html.Button(
                            "Export Processed Data",
                            id="btn-export-processed",
                        ),
                        # Add more content for this scenario
                        dcc.Download(id="download-processed-csv"),
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
                    id="visualisation-dashboard",
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
# Append Emails to Unclassified List - Remove Duplicates - Clear Upload Table
############################
@app.callback(
    [
        Output("table-unclassified-email", "children"),
        Output("output-cleaned-raw", "children", allow_duplicate=True),
    ],
    [
        Input("btn-add-to-unclassified-table", "n_clicks"),
        State("output-cleaned-raw", "children"),
        State("table-unclassified-email", "children"),
    ],
    prevent_initial_call=True,
)
def add_cleaned_emails_to_unclassified_table(
    clicks, raw_email_data_table, unclassified_table
):
    # if there isnt any uploaded emails don't update
    if raw_email_data_table is None:
        raise PreventUpdate
    else:
        tempRawDF = pd.DataFrame(raw_email_data_table["props"]["data"])
        # check if the unclassified table has been generated yet
        if unclassified_table is not None:
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
    Output("output-cleaned-raw", "children", allow_duplicate=True),
    Input("btn-clear-raw-output", "n_clicks"),
    State("output-cleaned-raw", "children"),
    prevent_initial_call=True,
)
def clear_raw_email_output(clicks, data_table):
    if data_table is None:
        raise PreventUpdate
    else:
        return None


############################
# Upload Cleaned Email CSV - Append - Display
############################
def load_preprocessed_csv(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            temp_df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), index_col=False)
        else:
            raise Exception
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
# Append Emails to Unclassified List - Remove Duplicates - Clear Upload Table
############################
@app.callback(
    [
        Output("table-unclassified-email", "children", allow_duplicate=True),
        Output("output-preprocessed-data", "children", allow_duplicate=True),
    ],
    [
        Input("btn-csv-to-unclassified", "n_clicks"),
        State("output-preprocessed-data", "children"),
        State("table-unclassified-email", "children"),
    ],
    prevent_initial_call=True,
)
def add_csv_to_unclassified_table(clicks, preprocessed_table, unclassified_table):
    # if there isnt any uploaded emails don't update
    if preprocessed_table is None:
        raise PreventUpdate
    else:
        # imported csv converted to dataframe converted to dash_table is wrapped in list - no solution right now, access first item in list first
        preprocessed_table = preprocessed_table[0]
        tempRawDF = pd.DataFrame(preprocessed_table["props"]["data"])

        # check if the unclassified table has been generated yet
        if unclassified_table is not None:
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
# Clear CSV Upload Table
############################
@app.callback(
    Output("output-preprocessed-data", "children", allow_duplicate=True),
    Input("btn-clear-csv", "n_clicks"),
    State("output-preprocessed-data", "children"),
    prevent_initial_call=True,
)
def clear_csv_output(clicks, data_table):
    if data_table is None:
        raise PreventUpdate
    else:
        return None


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
# Download Cleaned Emails to CSV
############################
# - WORKS
@app.callback(
    Output("download-cleaned-csv", "data"),
    Input("btn-download-cleaned", "n_clicks"),
    State("table-unclassified-email", "children"),
    prevent_initial_call=True,
)
def cleaned_data_to_file(n_clicks, data_table):
    # if data_table is none, prevent return
    if data_table is None:
        raise PreventUpdate
    else:
        # convert data table into a data frame so that it can be converted to a csv file
        tempDF = pd.DataFrame(data_table["props"]["data"])
        return dcc.send_data_frame(tempDF.to_csv, "cleaned_emails.csv", index=False)


############################
# Download Classified Emails to CSV
############################
@app.callback(
    Output("download-processed-csv", "data"),
    Input("btn-export-processed", "n_clicks"),
    State("output-sentiment", "children"),
    prevent_initial_call=True,
)
def cleaned_data_to_file(n_clicks, data_table):
    if data_table is None:
        raise PreventUpdate
    else:
        tempDF = pd.DataFrame(data_table["props"]["data"])
        return dcc.send_data_frame(tempDF.to_csv, "sentiment_classified_emails.csv")


############################
# Visualise Processed Emails
############################
# CREATE
@app.callback(
    Output("visualisation-dashboard", "children"),
    Input("output-sentiment", "children"),
)
def create_visualisations(data_table):
    if data_table is None:
        raise PreventUpdate
    else:
        # Get Sentiment Data
        sentimentDF = pd.DataFrame(data_table["props"]["data"])

        available_years = ["All Years"] + sentimentDF["Year"].unique().tolist()

        children = [
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
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="year-dropdown",
                            options=[
                                {"label": year, "value": year}
                                for year in available_years
                            ],
                            value="All Years",  # Default to "All Years"
                        )
                    ),
                ]
            ),
            dcc.Graph(
                id="visualization-graph",
                style={
                    "width": "100%",
                    "height": "700px",
                },  # Adjust the height as needed
            ),
        ]
    return children


# UPDATE - PARTIALLY WORKING
@app.callback(
    Output("visualization-graph", "figure"),
    Input("visualization-dropdown", "value"),
    Input("year-dropdown", "value"),
    State("output-sentiment", "children"),
)
def update_visualization(selected_option, selected_year, data_table):
    if data_table is None:
        raise PreventUpdate
    else:
        sentimentDF = pd.DataFrame(data_table["props"]["data"])
        # Make a copy
        sentiDF = sentimentDF


        # Create DF with a Value
        sentiDF["Value"] = np.select(
            [
                sentiDF["Labelled"] == "Positive",
                sentiDF["Labelled"] == "Neutral",
                sentiDF["Labelled"] == "Negative",
            ],
            [1, 0, -1],
        )
        
        
        filtered_df = sentiDF  # No filtering by year
        filtered_df_time_series = sentiDF[['Year', 'Month', 'Day', 'Value']]

        if selected_year != "All Years":
            filtered_df = sentiDF[sentiDF['Year'] == selected_year]
            filtered_df_time_series = filtered_df_time_series[filtered_df_time_series["Year"] == selected_year]

        df_wordCloud = filtered_df["Content"]
        df_network = filtered_df[['From','To']]

        if selected_option == "word-cloud":

            all_text = " ".join(df_wordCloud)

            wordcloud_data = generate_wordcloud(all_text)

            return wordcloud_data

        elif selected_option == "network-graph":
            # Generate and return a Network Graph visualization
            network_data = generate_network_graph(df_network)
            return network_data
        elif selected_option == "time-series":
            # Generate and return a Time Series visualization
            time_series_data = generate_time_series(filtered_df_time_series)
            return time_series_data
        elif selected_option == "tree-map":
            # Generate and return a Tree Map visualization
            tree_map_data = generate_tree_map(filtered_df)
            return tree_map_data
        elif selected_option == "pie-chart":
            # Generate and return a Pie Chart visualization
            pie_chart_data = generate_pie_chart(filtered_df)
            return pie_chart_data

# WORKS
def generate_wordcloud(content):
    # Generate the word cloud
    wordcloud = WordCloud(width=2000, height=1200, background_color="white").generate(
        content
    )

    # Create a BytesIO buffer to save the word cloud image
    buffer = io.BytesIO()

    # Save the word cloud image to the buffer
    plt.figure(figsize=(20, 12))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.title("Word Cloud")
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    # Encode the image as base64
    wordcloud_base64 = base64.b64encode(buffer.read()).decode()

    return {
        "data": [
            {
                "x": [0],
                "y": [0],
                "mode": "text",
                "text": ["Word Cloud"],
                "textfont": {"size": 24, "color": "black"},  # Customize text color
            }
        ],
        "layout": {
            "images": [
                {
                    "source": "data:image/png;base64,{}".format(wordcloud_base64),
                    "x": 0,
                    "y": 0,
                    "xref": "x",
                    "yref": "y",
                    "sizex": 1,
                    "sizey": 1,
                    "xanchor": "center",
                    "yanchor": "middle",
                }
            ],
            #"width": "auto",
            #"height": "auto",
            "xaxis": {"showgrid": False, "showticklabels": False, "zeroline": False},
            "yaxis": {"showgrid": False, "showticklabels": False, "zeroline": False},
        },
    }

# works
def generate_network_graph(df):
    G = nx.DiGraph()
    for index, row in df.iterrows():
        if (row["From"] is None):
            row['From'] = 'N/A'
        sender = row["From"]
        if (row['To'] is None):
            row['To'] = 'N/A'
        recipients = row["To"].split(", ")
        G.add_node(sender)
        for recipient in recipients:
            G.add_node(recipient)
            G.add_edge(sender, recipient)

    pos = nx.spring_layout(G, seed=42)
    edges = G.edges()
    edge_x = []
    edge_y = []
    for edge in edges:
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            )
        )
    )

    node_text = list(G.nodes())
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=0)
                    ))
    return fig



def generate_time_series(df):
    # Sort the DataFrame by 'Date' to ensure it's in the right order for plotting
    cols=['Year', 'Month', 'Day']
    df['Date'] = df[cols].apply(lambda x: '-'.join(x.values.astype(str)), axis='columns')
    df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d")
    df_sum = df.groupby('Date')['Value'].sum().reset_index()
    df_sum = df_sum.sort_values(by="Date")

    # Create a new DataFrame for the smoothed curve
    smooth_df = pd.DataFrame()
    num_dates = np.linspace(
        0, 1, len(df_sum)
    )  # Create a linear space of numerical dates between 0 and 1

    if len(df) >= 3:
    
        # Create a spline function
        spline = make_interp_spline(num_dates, df_sum["Value"], k=3)

        # Generate the numerical dates for the smoothed curve
        num_dates_smooth = np.linspace(
            0, 1, 100
        )  # Adjust the number of points (100 in this example)

        # Get the smoothed scores for the numerical dates
        scores_smooth = spline(num_dates_smooth)

        # Convert numerical dates back to actual dates
        smooth_dates = df_sum["Date"].min() + pd.to_timedelta(
            num_dates_smooth * (df_sum["Date"].max() - df_sum["Date"].min())
        )

        smooth_df["Date"] = smooth_dates
        smooth_df["Value"] = scores_smooth

    fig = px.scatter(df_sum, x="Date", y="Value", title="Score by Date")
    
    if len(df) >= 3:
        # Add the smoothed curve
        fig.add_scatter(
            x=smooth_df["Date"], y=smooth_df["Value"], mode="lines", name="Smoothed Curve"
        )

    return fig


def generate_tree_map(df):
    company_list = []
    for index, row in df.iterrows():
        
        recipients = row["To"].split(", ")  # get a list of recipients
        
        for recipient in recipients:
            parts = recipient.split("@")    # split the email by @

            #company_name = parts[1].split(".")[0]   # get the company name which is the string after @ before .

            try:
                company_name = parts[1].split(".")[0]
            except IndexError:
                company_name = ''


            if company_name != 'enron':
                company_list.append(company_name)   # add company name if it's not enron

    df_companies = pd.DataFrame({'Company Name': company_list})   # make a dataframe for plotting

    # Create a Tree Map for the selected year
    tree_map_fig = px.treemap(df_companies, path=['Company Name'], color='Company Name')
    return tree_map_fig


def generate_pie_chart(data_frame):
    # Generate and return a Pie Chart visualization
    label_counts = data_frame["Labelled"].value_counts()

    labels = label_counts.index
    values = label_counts.values

    pie_chart_data = {
        "data": [
            {
                "type": "pie",
                "labels": labels,
                "values": values,
            }
        ],
        "layout": {"title": "Distribution of Labels"},
    }
    return pie_chart_data


############################
# INIT -> RUNS THE PROGRAM #
############################
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)