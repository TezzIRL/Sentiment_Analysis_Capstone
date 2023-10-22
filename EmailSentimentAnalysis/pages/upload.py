# handles all logic for the upload page

# uses code from dash upload example

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
import datetime
import io

from ESA_Modules import Preprocessor

import pandas as pd

email_preprocessor = Preprocessor()

register_page(__name__, top_nav=True, path="/upload")

def layout():
    layout = html.Div(
        [
            dcc.Upload(
                id="upload-data",
                children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
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
        ]
    )

    return layout


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
        email_preprocessor.CleanEmails(unprocessed_email)

    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    return html.Div(
        [
            html.H5(filename),
            html.H6(datetime.datetime.fromtimestamp(date)),
            dash_table.DataTable(
                data = email_preprocessor.get_dataframe().to_dict('records'),
                columns = [{'name': i, 'id': i} for i in email_preprocessor.get_dataframe().columns],
                style_data = {
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                fill_width=False
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